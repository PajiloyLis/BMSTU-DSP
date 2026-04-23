import numpy as np
import matplotlib.pyplot as plt


def mygaussignal(x):
    a = 1
    sigma = 1
    return a * np.exp(-(x ** 2) / (sigma ** 2))


def mean_filter_value(ux, i):
    # среднее по 5 точкам: 2 слева, текущая, 2 справа
    r = 0
    imin = i - 2
    imax = i + 2

    for j in range(imin, imax + 1):
        if 0 <= j < len(ux):
            r += ux[j]

    r = r / 5
    return r


def med(ux, i):
    # аналог MATLAB-функции: возвращает меньшее из соседних значений
    imin = i - 1
    imax = i + 1

    if imin < 0:
        return ux[imax]
    elif imax >= len(ux):
        return ux[imin]
    else:
        if ux[imax] > ux[imin]:
            return ux[imin]
        else:
            return ux[imax]


def lab_08():
    F = 3
    dt = 0.05
    x = np.arange(-F, F + dt, dt)

    yx = mygaussignal(x)
    uxbase = mygaussignal(x).copy()
    ux = mygaussignal(x).copy()
    N = len(yx)

    a = 0.25
    epsv = 0.05

    px = a * np.random.rand(7)

    # MATLAB-индексы были с 1, в Python делаем с 0
    pos = [24, 34, 39, 53, 66, 74, 94]
    pxx = len(pos)

    # добавляем шум
    for i in range(pxx):
        ux[pos[i]] += px[i]
        uxbase[pos[i]] += px[i]

    # mean-фильтрация
    for i in range(N):
        smthm = mean_filter_value(ux, i)
        if abs(ux[i] - smthm) > epsv:
            ux[i] = smthm

    plt.figure()
    plt.title("MEAN-функция фильтрации")
    plt.plot(x, yx, label="Исходный гауссовский сигнал")
    plt.plot(x, uxbase, label="Искаженный сигнал")
    plt.plot(x, ux, label="Сглаженный сигнал")
    plt.legend()
    plt.grid(True)

    # заново генерируем сигналы
    uxbase = mygaussignal(x).copy()
    ux = mygaussignal(x).copy()

    for i in range(pxx):
        ux[pos[i]] += px[i]
        uxbase[pos[i]] += px[i]

    # med-фильтрация
    for i in range(N):
        smthm = med(uxbase, i)
        if abs(ux[i] - smthm) > epsv:
            ux[i] = smthm

    plt.figure()
    plt.title("MED-функция фильтрации")
    plt.plot(x, yx, label="Исходный гауссовский сигнал")
    plt.plot(x, uxbase, label="Искаженный сигнал")
    plt.plot(x, ux, label="Сглаженный сигнал")
    plt.legend()
    plt.grid(True)

    plt.show()


if __name__ == "__main__":
    lab_08()