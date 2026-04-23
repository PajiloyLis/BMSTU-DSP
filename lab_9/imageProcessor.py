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

def estimate_motion_blur_parameters(cep, threshold=0.5):
    """
    Оценка длины и угла смаза по кепстру.
    Возвращает (d, angle_deg) – длина в пикселях и угол направления смаза.
    """
    h, w = cep.shape
    center = (h//2, w//2)
    # Обнуляем центральную область (DC)
    mask_radius = 5
    cep_peaks = cep.copy()
    cep_peaks[center[0]-mask_radius:center[0]+mask_radius,
              center[1]-mask_radius:center[1]+mask_radius] = 0
    # Ищем глобальный максимум
    max_idx = np.unravel_index(np.argmax(cep_peaks), cep_peaks.shape)
    dx = max_idx[0] - center[0]
    dy = max_idx[1] - center[1]
    d = np.sqrt(dx**2 + dy**2)
    # Угол направления смаза перпендикулярен вектору (dx, dy)
    angle = np.arctan2(dy, dx) * 180 / np.pi
    blur_angle = angle + 90
    # Нормализуем угол в [0,180)
    blur_angle = blur_angle % 180
    return d, blur_angle

def estimate_defocus_radius(cep):
    """Оценка радиуса дефокусировки по радиальному профилю кепстра"""
    h, w = cep.shape
    center = (h//2, w//2)
    max_radius = min(h,w)//2 - 10
    radial_profile = []
    for r in range(1, max_radius):
        y, x = np.ogrid[:h, :w]
        mask = (np.hypot(y-center[0], x-center[1]) >= r-0.5) & \
               (np.hypot(y-center[0], x-center[1]) < r+0.5)
        radial_profile.append(np.mean(cep[mask]))
    radial_profile = np.array(radial_profile)
    # Ищем первый значимый пик (максимум после небольшого подъёма)
    # Для простоты берём индекс глобального максимума
    radius = np.argmax(radial_profile) + 1
    return radius

def create_motion_blur_psf(size, length, angle):
    """
    size: (height, width) кортеж
    length: длина смаза в пикселях
    angle: угол направления смаза (градусы)
    """
    psf = np.zeros(size)
    h, w = size
    c_y, c_x = h//2, w//2
    rad = np.deg2rad(angle)
    dx = length * np.cos(rad)
    dy = length * np.sin(rad)
    x1 = int(round(c_x - dx/2))
    y1 = int(round(c_y - dy/2))
    x2 = int(round(c_x + dx/2))
    y2 = int(round(c_y + dy/2))
    # Рисуем линию (метод Брезенхема)
    from skimage.draw import line
    rr, cc = line(y1, x1, y2, x2)
    mask = (rr >= 0) & (rr < h) & (cc >= 0) & (cc < w)
    psf[rr[mask], cc[mask]] = 1
    psf = psf / np.sum(psf)
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

def wiener_deconvolution(img, psf, K=0.01):
    """Фильтр Винера для 2D"""
    F_img = fftpack.fft2(img)
    F_psf = fftpack.fft2(psf, shape=img.shape)
    H_conj = np.conj(F_psf)
    denominator = np.abs(F_psf)**2 + K
    F_restored = F_img * H_conj / denominator
    restored = np.real(fftpack.ifft2(F_restored))
    restored = np.fft.fftshift(restored) 
    return np.clip(restored, 0, 1)

# Альтернативно, можно использовать skimage.restoration.richardson_lucy