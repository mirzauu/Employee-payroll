"""
    Rule Class
"""
from apps.clients.models import EarningsComponent, DeductionComponent
from apps.clients.models import ClientSalarySettings, Client
from dataclasses import dataclass, field


class BaseRule(object):

    def __init__(self, data, deductions, attendance, bonus_choice=False, bonus_value=None, **kwargs):
        self._data = {}
        self.attendance = attendance
        self._deductions = deductions
        self.bonus_choice = bonus_choice
        self.bonus_value = bonus_value
        if data:
            for key, value in data.items():
                if isinstance(value, dict):
                    for i, j in value.items():
                        _key, _value = self.get_earnings_components(i, j, attendance)
                        setattr(self, _key, int(_value))
                        self._data[_key] = int(_value)
                elif value is not None:
                    self._data[key] = self.get_monthly_value(value, attendance)
                    setattr(self, key, int(value))
        print('data', self._data)

    @staticmethod
    def get_earnings_components(key, value, attendance):
        return key, (float(value) * int(attendance))

    @staticmethod
    def get_monthly_value(value, attendance):
        if value is not None:
            return float(value) * int(attendance)
        else:
            return 0

    def get_deduction_components(self):
        _deduction = {
            'pf': self.get_pf(),
            'esi': self.get_esi()
        }
        for key, value in self._deductions.items():
            if value is not None:
                if not isinstance(value, dict):
                    _deduction[key] = float(value)
                else:
                    for i, j in value.items():
                        _deduction[i] = float(j)
        return _deduction

    def get_total_deductions(self):
        _total = 0
        grand_deduction = self.get_deduction_components()
        for key, value in grand_deduction.items():
            _total += int(value)
        print('total', _total)
        return _total

    def get_data(self):
        if self.bonus_choice == 'percentage':
            self._data['bonus_pay'] = self.get_bonus_pay()
        elif self.bonus_value == 'value':
            self._data['bonus_pay'] = int(self.bonus_value) * int(self.attendance)
        return self._data

    def get_additional_pay(self):
        if hasattr(self, 'add_pay'):
            if self.add_pay > 0:
                return self.add_pay * 2
        return 0

    def get_bonus_pay(self):
        value = self.bonus_value
        return round((int(value) / 100) * self.get_basic_vda())

    def get_basic_vda(self):
        if hasattr(self, 'basic_vda'):
            return int(self.basic_vda) * int(self.attendance)
        else:
            return 0

    def get_nfh(self):
        if hasattr(self, 'nfh'):
            return self.nfh * self.attendance
        else:
            return 0

    def get_bonus(self):
        if hasattr(self, 'bonus'):
            return self.bonus * self.attendance
        else:
            return 0

    def get_pf(self):
        if hasattr(self, 'basic_vda'):
            return round((12 / 100) * 15000)
        else:
            return 0

    def get_esi(self):
        if int(self.get_basic_vda()) < 20000:
            return round((0.75 / 100) * self.get_basic_vda())
        else:
            return 0

    def get_earning_total(self):
        _total = 0
        for value in self._data.values():
            _total += float(value)
        return _total

    def __call__(self, *args, **kwargs):
        return self.get_data()


@dataclass(slots=True)
class DPRule:

    earn: dict
    deduct: dict
    attendance: dict
    _data: dict = field(default_factory=dict)
    extra_dict: dict = field(default_factory=dict)
    civil_guard: int = None
    container_operator: int = None
    ex_service_guard: int = None
    supervisor: int = None
    senior_supervisor: int = None

    @classmethod
    def _change_atr(cls, instance, key, value):
        setattr(instance, key, value)

    def _get_service_attendance(self):
        for key, value in self.attendance.items():
            self._change_atr(self, key, value)

    def _get_civil_value(self, value):
        return round(float(value)) * self.civil_guard

    def _get_earnings(self):
        self._get_service_attendance()
        for key, value in self.earn.items():
            if isinstance(value, dict):
                for i, j in value.items():
                    if i == 'container_operator' or i == 'supervisor':
                        self.extra_dict[i] = j
                    elif self.civil_guard:
                        self._data[i] = float(j) * float(self.civil_guard)
                    else:
                        self._data[i] = float(j) * float(self.ex_service_guard)
            elif self.civil_guard:
                self._data[key] = float(value) * float(self.civil_guard)
            else:
                self._data[key] = float(value) * float(self.ex_service_guard)
        return self._data

    def get_epf(self):
        return round(float(12 / 100) * 15000)

    def get_esi(self):
        return round(float(0.75 / 100) * self._data['basic_vda'])

    def get_deduction_components(self):
        _data = self._get_earnings()
        _deduction = {
            'pf': self.get_epf(),
            'esi': self.get_esi() if self.get_esi() > 20000 else 0
        }
        for key, value in self.deduct.items():
            if value is not None:
                _deduction[key] = float(value)
        return _deduction

    def get_total_deductions(self):
        _total = 0
        grand_deduction = self.get_deduction_components()
        for key, value in grand_deduction.items():
            _total += int(value)
        return _total

    def get_earning_total(self):
        _total = 0
        for key, value in self._data.items():
            _total += float(value)
        return _total
        
    def get_data(self):
        _earnings = self._get_earnings()
        for key, value in self.extra_dict.items():
            if key == 'container_operator':
                _earnings[key] = float(self.extra_dict[key]) * float(self.container_operator)
            elif key == 'supervisor':
                _earnings[key] = float(self.extra_dict[key]) * float(self.supervisor)
        return _earnings

    def __call__(self, *args, **kwargs):
        return self.get_data()
