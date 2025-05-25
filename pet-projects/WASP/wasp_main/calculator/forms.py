from django import forms


class WaterPropertiesForm(forms.Form):
    mode = forms.ChoiceField(choices=[('saturation', 'Линия насыщения'), ('full', 'Вся область')], label="Режим")
    pressure = forms.FloatField(required=False, label="Давление P (МПа)", min_value=0.0)
    temperature = forms.FloatField(required=False, label="Температура T (°C)", min_value=-273.15)
    enthalpy = forms.FloatField(required=False, label="Энтальпия H (кДж/кг)")
    calc_by = forms.ChoiceField(choices=[('P', 'P'), ('T', 'T')], required=False, label="Рассчитать по")
    param_type = forms.ChoiceField(choices=[
        ('P-H', 'P-H'),
        ('P-T-water', 'P-T - вода'),
        ('P-T-steam', 'P-T - сухой пар')
    ], required=False, label="Задаваемые параметры")

    def clean(self):
        cleaned_data = super().clean()
        mode = cleaned_data.get('mode')
        pressure = cleaned_data.get('pressure')
        temperature = cleaned_data.get('temperature')
        enthalpy = cleaned_data.get('enthalpy')
        calc_by = cleaned_data.get('calc_by')
        param_type = cleaned_data.get('param_type')

        if mode == 'saturation':
            if not calc_by:
                raise forms.ValidationError("Выберите, рассчитывать по P или T.")
            if calc_by == 'P':
                if pressure is None:
                    raise forms.ValidationError("Введите давление для расчёта по P.")
                if pressure <= 0:
                    raise forms.ValidationError("Давление должно быть больше 0.")
            elif calc_by == 'T':
                if temperature is None:
                    raise forms.ValidationError("Введите температуру для расчёта по T.")
                if temperature <= 0:
                    raise forms.ValidationError("Температура должна быть больше 0 для линии насыщения.")
        elif mode == 'full':
            if not param_type:
                raise forms.ValidationError("Выберите пару параметров.")
            if param_type == 'P-H':
                if pressure is None:
                    raise forms.ValidationError("Введите давление для P-H.")
                if enthalpy is None:
                    raise forms.ValidationError("Введите энтальпию для P-H.")
                if pressure <= 0:
                    raise forms.ValidationError("Давление должно быть больше 0.")
            elif param_type in ['P-T-water', 'P-T-steam']:
                if pressure is None:
                    raise forms.ValidationError("Введите давление для P-T.")
                if temperature is None:
                    raise forms.ValidationError("Введите температуру для P-T.")
                if pressure <= 0:
                    raise forms.ValidationError("Давление должно быть больше 0.")

        return cleaned_data
