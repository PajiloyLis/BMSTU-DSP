% ==================== blind_deconv_octave.m ====================
% Автоматическое определение параметров PSF и восстановление
% Для Octave с пакетом image

pkg load image;

% ---------- 1. Загрузка изображения ----------
img_name = 'filblind.jpg';   % замените на ваш файл
I = im2double(imread(img_name));
figure('Name', 'Искажённое изображение');
imshow(I); title('Искажённое изображение');

% ---------- 2. Вычисление кепстра ----------
F = fft2(I);
log_power = log1p(abs(F).^2);
cepstrum = real(ifft2(log_power));
cepstrum = fftshift(cepstrum);   % центр в середине
figure('Name', 'Кепстр');
imshow(cepstrum, []); title('Кепстр (логарифмический)');
% ---------- 3. Выбор типа искажения ----------
% Раскомментируйте ОДИН из блоков:
tipo = 'motion';      % для смаза
% tipo = 'defocus';   % для дефокусировки

% ---------- 4. Автооценка параметров ----------
if strcmp(tipo, 'motion')
    % === Смаз (motion blur) ===
    % Ищем два симметричных пика в кепстре
    [h, w] = size(cepstrum);
    center = [h/2, w/2];
    % Обнуляем центральную область (диаметр 5 пикселей)
    cep_peaks = cepstrum;
    cep_peaks(center(1)-2:center(1)+2, center(2)-2:center(2)+2) = 0;
    % Ищем глобальный максимум
    [max_val, idx] = max(cep_peaks(:));
    [y, x] = ind2sub([h,w], idx);
    dx = x - center(2);
    dy = y - center(1);
    d = sqrt(dx^2 + dy^2);            % длина смаза в пикселях
    angle = atan2d(dy, dx);           % угол вектора от центра к пику
    blur_angle = angle + 90;          % направление смаза (перпендикуляр)
    blur_angle = mod(blur_angle, 180);
    printf('Автооценка: длина смаза = %.1f пикс, угол = %.1f°\n', d, blur_angle);
    
    % Создание PSF для смаза
    PSF = fspecial('motion', round(13), -45);
    
elseif strcmp(tipo, 'defocus')
    % === Дефокусировка ===
    % Радиальный профиль кепстра
    [h, w] = size(cepstrum);
    center = [h/2, w/2];
    max_radius = floor(min(h,w)/2) - 5;
    radial_vals = zeros(1, max_radius);
    for r = 1:max_radius
        mask = ( ( (1:h) - center(1)).^2 + ((1:w) - center(2)).^2 ) <= (r+0.5)^2 & ...
               ( ( (1:h) - center(1)).^2 + ((1:w) - center(2)).^2 ) >= (r-0.5)^2;
        radial_vals(r) = mean(cepstrum(mask));
    end
    % Сглаживание профиля
    radial_vals_smooth = smooth(radial_vals, 5);
    % Ищем первый локальный максимум после центра (начиная с r=2)
    [pks, locs] = findpeaks(radial_vals_smooth, 'MinPeakHeight', mean(radial_vals_smooth(1:5)));
    if isempty(locs)
        radius = 5;   % значение по умолчанию
    else
        radius = locs(1);   % первый пик
    end
    printf('Автооценка: радиус дефокусировки = %d пикс\n', radius);
    
    % Создание PSF для дефокусировки (диск)
    PSF = fspecial('disk', radius);
end

% ---------- 5. Восстановление фильтром Винера ----------
% Параметр NSR (шум/сигнал) – подберите вручную для лучшего результата
NSR = 0.02;   % для смаза; для дефокусировки можно 0.001..0.05
J_wiener = deconvwnr(I, PSF, NSR);

figure('Name', 'Восстановленное (Wiener)');
imshow(J_wiener); title(sprintf('Восстановленное (Wiener, NSR=%.3f)', NSR));
pause;
% ---------- 6. Альтернативно: регуляризованный фильтр ----------
reg_param = 0.001;
J_reg = deconvreg(I, PSF, reg_param);
figure('Name', 'Восстановленное (регуляризованное)');
imshow(J_reg); title(sprintf('Регуляризованное (reg=%.4f)', reg_param));

% ---------- 7. Сохранение результата (опционально) ----------
imwrite(J_wiener, 'restored_wiener.bmp');
imwrite(J_reg, 'restored_reg.bmp');
printf('\nРезультаты сохранены в restored_wiener.bmp и restored_reg.bmp\n');

% ---------- Ожидание, чтобы окна не закрылись ----------
input('Нажмите Enter, чтобы завершить...');