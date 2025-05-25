from django.shortcuts import render
from .forms import WaterPropertiesForm
from iapws import IAPWS97

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def calculate_properties(request):
    form = WaterPropertiesForm(request.POST or None)
    result = None
    error = None

    if request.method == 'POST':
        if form.is_valid():
            mode = form.cleaned_data['mode']
            pressure = form.cleaned_data['pressure']
            temperature = form.cleaned_data['temperature']
            enthalpy = form.cleaned_data['enthalpy']
            calc_by = form.cleaned_data['calc_by']
            param_type = form.cleaned_data['param_type']

            try:
                if mode == 'saturation':
                    if calc_by == 'P':
                        if not (0.000611 < pressure < 22.064):
                            raise ValueError("Давление должно быть в диапазоне 0.000611–22.064 МПа")
                        water = IAPWS97(P=pressure, x=0)
                        steam = IAPWS97(P=pressure, x=1)
                        result = {
                            'P': pressure,  # Введённое давление
                            'T': water.T - 273.15,  # Температура из IAPWS97
                            'water': {
                                'h': water.h, 's': water.s, 'v': water.v,
                                'rho': water.rho, 'mu': water.mu, 'nu': water.mu / water.rho
                            },
                            'steam': {
                                'h': steam.h, 's': steam.s, 'v': steam.v,
                                'rho': steam.rho, 'mu': steam.mu, 'nu': steam.mu / steam.rho
                            }
                        }
                    else:  # calc_by == 'T'
                        if not (0 < temperature < 373.946):
                            raise ValueError("Температура должна быть в диапазоне 0–373.946 °C")
                        water = IAPWS97(T=temperature + 273.15, x=0)
                        steam = IAPWS97(T=temperature + 273.15, x=1)
                        result = {
                            'P': water.P,  # Давление из IAPWS97
                            'T': temperature,  # Введённая температура
                            'water': {
                                'h': water.h, 's': water.s, 'v': water.v,
                                'rho': water.rho, 'mu': water.mu, 'nu': water.mu / water.rho
                            },
                            'steam': {
                                'h': steam.h, 's': steam.s, 'v': steam.v,
                                'rho': steam.rho, 'mu': steam.mu, 'nu': steam.mu / steam.rho
                            }
                        }
                elif mode == 'full':
                    if param_type == 'P-H':
                        if not (0.000611 < pressure < 100):
                            raise ValueError("Давление должно быть в диапазоне 0.000611–100 МПа")
                        water = IAPWS97(P=pressure, h=enthalpy)
                    elif param_type == 'P-T-water':
                        if not (0.000611 < pressure < 100):
                            raise ValueError("Давление должно быть в диапазоне 0.000611–100 МПа")
                        water = IAPWS97(P=pressure, T=temperature + 273.15, x=0)
                    elif param_type == 'P-T-steam':
                        if not (0.000611 < pressure < 100):
                            raise ValueError("Давление должно быть в диапазоне 0.000611–100 МПа")
                        water = IAPWS97(P=pressure, T=temperature + 273.15, x=1)
                    result = {
                        'P': water.P, 'T': water.T - 273.15, 'h': water.h, 's': water.s,
                        'v': water.v, 'rho': water.rho, 'x': water.x if water.x is not None else 'N/A',
                        'mu': water.mu, 'nu': water.mu / water.rho
                    }
            except Exception as e:
                error = f"Ошибка в расчётах: {str(e)}"

    return render(request, 'calculator/calculate.html', {'form': form, 'result': result, 'error': error})