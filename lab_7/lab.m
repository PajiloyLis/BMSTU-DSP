function main()
    % Начальные значения
    A = 1.0;
    NS = 0.05;
    s1 = 1.0;
    s2 = 2.0;
    mult = 6;
    step = 0.009;
    t = -mult:step:mult;

    % Гауссов импульс
    u1 = A * exp(-(t/s1).^2);
    u2 = A * exp(-(t/s2).^2);

    v1 = fft(u1);
    v2 = fft(u2);

    % Помехи
    n1 = unifrnd(-NS, NS, 1, length(t));
    n2 = unifrnd(-NS, NS, 1, length(t));

    delta = std(n1);
    epsilon = std(n2);

    figure;

    hold on;
    grid on;
    plot(t, u1+n1, 'r');
    plot(t, u2+n2, 'g');
    plot(t, abs(ifft(fft(u2+n2) .* tikhonov_filter(v1, v2, step, 2 * mult, delta, epsilon))), 'b')
    legend('Неискаженный сигнал', 'Искаженныый сигнал', 'Функция импульсного отклика');
end

function h = tikhonov_filter(u1, u2, step, T, d, e)
    m = 0:length(u1)-1;
    mult = step / length(u1);
    squ = 1 + (2 * pi * m / T).^2;
    func = @(x) rho(x, u1, u2, step, T, d, e);
    alpha = fzero(func, [0, 1]);
    h = 0:length(u1)-1;
    for k = 1:length(h)
      h(k) = mult * sum(exp(2 * pi * 1i * k .* m / length(u1)) .* u1 .* conj(u2) ./ (abs(u2).^2 .* step^2 + alpha * squ), 2);
    end
end

function y = rho(x, u1, u2, step, T, d, e)
    m = 0:length(u1)-1;
    mult = step / length(u1);
    squ = 1 + (2 * pi * m / T).^2;
    beta = mult * sum(x.^2 * squ .* abs(u1).^2 ./ (abs(u2).^2 * step^2 + x .* squ).^2, 2);
    gamma = mult * sum(abs(u2).^2 * step^2 .* abs(u1).^2 .* squ ./ (abs(u2).^2 * step^2 + x * (1 + 2 * pi * m / T).^2).^2, 2);
    y = beta - (d + e * sqrt(gamma))^2;
end