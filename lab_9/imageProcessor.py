import numpy as np
from scipy import fftpack
from skimage import restoration

def compute_cepstrum(img):
    """Возвращает кепстр изображения (2D)"""
    F = fftpack.fft2(img)
    power = np.abs(F)**2
    log_power = np.log1p(power)   # log(1+power)
    c = np.real(fftpack.ifft2(log_power))
    return fftpack.fftshift(c)

def estimate_motion_blur_parameters(cep, min_length=3, max_length=None):
    h, w = cep.shape
    if max_length is None:
        max_length = min(h, w) // 2
    center = (h//2, w//2)
    # Обнуляем центр (DC)
    cep_peaks = cep.copy()
    cep_peaks[center[0]-5:center[0]+5, center[1]-5:center[1]+5] = 0
    # Применяем порог, например, 70% от максимума
    threshold = 0.7 * np.max(cep_peaks)
    # Находим все пики выше порога
    from scipy.ndimage import label, center_of_mass
    label_mask = cep_peaks > threshold
    labeled, num_features = label(label_mask)
    if num_features == 0:
        return min_length, 0.0
    # Для каждого пика вычисляем расстояние и угол, выбираем наиболее подходящий
    best_d = min_length
    best_angle = 0.0
    best_score = 0
    for i in range(1, num_features+1):
        yc, xc = center_of_mass(cep_peaks, labeled, i)
        dy = yc - center[0]
        dx = xc - center[1]
        d = np.hypot(dx, dy)
        if d < min_length or d > max_length:
            continue
        angle = np.arctan2(dy, dx) * 180 / np.pi
        blur_angle = (angle + 90) % 180
        score = cep_peaks[int(round(yc)), int(round(xc))]
        if score > best_score:
            best_score = score
            best_d = d
            best_angle = blur_angle
    return best_d, best_angle

def estimate_defocus_radius(cep):
    h, w = cep.shape
    center = (h//2, w//2)
    max_radius = min(h, w) // 2 - 5
    radial_profile = []
    for r in range(1, max_radius):
        y, x = np.ogrid[:h, :w]
        mask = (np.hypot(y-center[0], x-center[1]) >= r-0.5) & \
               (np.hypot(y-center[0], x-center[1]) < r+0.5)
        radial_profile.append(np.mean(cep[mask]))
    radial_profile = np.array(radial_profile)
    # Сглаживание профиля для уменьшения шума
    from scipy.signal import savgol_filter
    smoothed = savgol_filter(radial_profile, window_length=5, polyorder=2)
    # Ищем первый локальный максимум, который превышает среднее
    threshold = np.mean(smoothed[:5])   # среднее вблизи центра
    for i in range(1, len(smoothed)-1):
        if smoothed[i] > smoothed[i-1] and smoothed[i] > smoothed[i+1] and smoothed[i] > threshold:
            return i + 1   # +1, т.к. массив с r=1
    return np.argmax(radial_profile) + 1   # fallback

def estimate_wiener_k(psf, snr_db=30):
    psf_fft = fftpack.fft2(psf)
    signal_power = np.mean(np.abs(psf_fft)**2)
    noise_power = signal_power / (10**(snr_db/10))
    return noise_power / signal_power

def create_motion_blur_psf(size, length, angle):
    psf = np.zeros(size)
    h, w = size
    c_y, c_x = h//2, w//2
    rad = np.deg2rad(-angle)   # инвертируем для координат изображения
    dx = length * np.cos(rad)
    dy = length * np.sin(rad)
    x1 = int(round(c_x - dx/2))
    y1 = int(round(c_y - dy/2))
    x2 = int(round(c_x + dx/2))
    y2 = int(round(c_y + dy/2))
    from skimage.draw import line
    rr, cc = line(y1, x1, y2, x2)
    valid = (rr >= 0) & (rr < h) & (cc >= 0) & (cc < w)
    psf[rr[valid], cc[valid]] = 1
    psf /= np.sum(psf)
    return psf

def create_defocus_psf(size, radius):
    psf = np.zeros(size)
    h, w = size
    c_y, c_x = h//2, w//2
    y, x = np.ogrid[:h, :w]
    mask = (x - c_x)**2 + (y - c_y)**2 <= radius**2
    psf[mask] = 1
    psf = psf / np.sum(psf)
    return psf

def wiener_deconvolution(img, psf, K=None):
    if K is None:
        K = estimate_wiener_k(psf)
    F_img = fftpack.fft2(img)
    F_psf = fftpack.fft2(psf, shape=img.shape)
    H_conj = np.conj(F_psf)
    denominator = np.abs(F_psf)**2 + K
    F_restored = F_img * H_conj / denominator
    restored = np.real(fftpack.ifft2(F_restored))
    restored = np.fft.fftshift(restored)
    return np.clip(restored, 0, 1)

# В imageProcessor.py
def richardson_lucy_deconvolution(img, psf, iterations=1, K=0.01):
    """
    Итерационная деконволюция Ричардсона-Люси.
    K – малая константа для стабилизации (можно 0, но лучше 1e-6).
    """
    from scipy.signal import convolve2d
    img = img.astype(np.float64)
    psf = psf.astype(np.float64)
    # Нормализация PSF
    psf /= psf.sum()
    # Начальное приближение
    est = img.copy()
    psf_mirror = np.flip(psf)
    for _ in range(iterations):
        # Свёртка текущей оценки с PSF
        conv = convolve2d(est, psf, mode='same', boundary='wrap')
        # Относительная ошибка
        rel_err = img / (conv + K)
        # Корректировка
        est = est * convolve2d(rel_err, psf_mirror, mode='same', boundary='wrap')
    return np.clip(est, 0, 1)