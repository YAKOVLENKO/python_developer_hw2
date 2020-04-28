import pandas as pd
import os
import logging
import re
from datetime import datetime
from calendar import monthrange


class LogDescriptor:
    def __init__(self, file_path, log_name, log_level):
        self.__log = logging.getLogger(log_name)
        self.__log.setLevel(log_level)

        self.__handler = logging.FileHandler(file_path, encoding='utf-8', delay=True)
        # self.__handler = logging.FileHandler(file_path, encoding='utf-8')
        h_format = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
        self.__handler.setFormatter(h_format)

        self.__log.addHandler(self.__handler)
        self.__message_func = self._get_message_func(log_level)

    def write(self, string):
        self.__handler.emit(string)
        self.__message_func(string)
        self.__handler.close()

    def _get_message_func(self, log_level):
        if log_level == 'INFO':
            return self.__log.info
        return self.__log.error


class Patient:
    __document_types = {'паспорт': 10,
                        'заграничный паспорт': 9,
                        'водительское удостоверение': 10}

    __ERROR_LOG = LogDescriptor('errors.log', 'error', 'ERROR')
    __INFO_LOG = LogDescriptor('info.log', 'info', 'INFO')

    def __init__(self, first_name, last_name, birth_date, phone, document_type, document_id):
        self.__first_name = self._get_correct_name(first_name)
        self.__last_name = self._get_correct_name(last_name)
        self.__birth_date = self._get_correct_birth_date(birth_date)
        self.__phone = self._get_correct_phone(phone)
        self.__document_type = self._get_correct_document_type(document_type)
        self.__document_id = self._get_correct_document_id(document_id)
        self.__INFO_LOG.write(f"New user has created: {self.__get_username()}")

    def __str__(self):
        return (f"Имя: {self.__first_name}\n"
                f"Фамилия: {self.__last_name}\n"
                f"Дата рождения: {self.__birth_date}\n"
                f"Телефон: {self.__phone}\n"
                f"Тип документа: {self.__document_type}\n"
                f"Номер документа: {self.__document_id}\n")

    def __getattr__(self, item):
        return False

    def __get_username(self):
        username = 'New User'
        if self.__first_name and self.__last_name:
            username = f"User {self.__first_name + ' ' + self.__last_name}"
        return username

    @property
    def first_name(self):
        return self.__first_name

    @first_name.setter
    def first_name(self, first_name):
        self.__ERROR_LOG.write(f"Attempt to change first name: {self.__get_username()}")
        raise AttributeError(f"Attempt to change first name: {self.__get_username()}")

    @property
    def last_name(self):
        return self.__last_name

    @last_name.setter
    def last_name(self, last_name):
        message = f"Attempt to change last name: {self.__get_username()}"
        self.__ERROR_LOG.write(message)
        raise AttributeError(message)

    @property
    def birth_date(self):
        return self.__birth_date

    @birth_date.setter
    def birth_date(self, birth_date):
        self.__birth_date = self._get_correct_birth_date(birth_date)
        self.__INFO_LOG.write(f"Birth date field change: {self.__get_username()}")

    @property
    def phone(self):
        return self.__phone

    @phone.setter
    def phone(self, phone):
        self.__phone = self._get_correct_phone(phone)
        self.__INFO_LOG.write(f"Phone field change: {self.__get_username()}")

    @property
    def document_type(self):
        return self.__document_type

    @document_type.setter
    def document_type(self, document_type):
        self.__document_type = self._get_correct_document_type(document_type)
        self.__INFO_LOG.write(f"Document type field change: {self.__get_username()}")

    @property
    def document_id(self):
        return self.__document_id

    @document_id.setter
    def document_id(self, document_id):
        self.__document_id = self._get_correct_document_id(document_id)
        self.__INFO_LOG.write(f"Document id field change: {self.__get_username()}")

    def _check_if_is_str(self, value):
        if type(value) != str:
            self.__ERROR_LOG.write(f"Attempt to set a value with a wrong type ({value}): {self.__get_username()}")
            raise TypeError('Attempt to set a value with a wrong type')
        return True

    def _check_date_validity(self, value_list):
        year, month, day = value_list
        if year < 1870:
            self.__ERROR_LOG.write(f"Attempt to set invalid year ({year}): {self.__get_username()}")
            raise ValueError("People can not be so  old")
        if year > datetime.now().year:
            self.__ERROR_LOG.write(f"Attempt to set invalid year ({year}): {self.__get_username()}")
            raise ValueError("This year will be available in future")
        if month > 12:
            self.__ERROR_LOG.write(f"Attempt to set invalid month ({month}): {self.__get_username()}")
            raise ValueError('There are only 12 months in year')
        if day > monthrange(year, month)[1]:
            self.__ERROR_LOG.write(f"Attempt to set invalid day ({day}): {self.__get_username()}")
            raise ValueError(f'There are only {monthrange(year, month)} days in this month')
        if datetime(year, month, day) > datetime.now():
            self.__ERROR_LOG.write(f"""Attempt to set invalid date ({datetime(year, month, day)}): 
                                       {self.__get_username()}""")
            raise ValueError('This birth date will be available in future')
        return True

    def _get_correct_name(self, name):
        if self._check_if_is_str(name):
            for char in name:
                if not char.isalpha():
                    self.__ERROR_LOG.write(f"Attempt to set value with incorrect symbol as name ({name}): New User")
                    raise ValueError('All symbols in first name and second name must be letters')
            return name.title()

    def _get_correct_birth_date(self, birth_date):
        if self._check_if_is_str(birth_date):
            birth_date = re.findall(r'\d+', birth_date)
            if len(birth_date) != 3:
                self.__ERROR_LOG.write(f"Attempt to set incomplete information about birth date ({birth_date}): "
                                       f"{self.__get_username()}")
                raise ValueError('Birth date information is not full')

            if len(birth_date[2]) == 4:
                birth_date = reversed(birth_date)
            birth_date = [int(val) for val in birth_date]

            if self._check_date_validity(birth_date):
                return datetime(*birth_date).strftime("%Y-%m-%d")

    def _get_correct_phone(self, phone):
        if self._check_if_is_str(phone):
            if not phone.isdecimal():
                phone = re.findall(r'\d+', phone)
                phone = ''.join(phone)
            if len(phone) == 11:
                if phone[0] != '7' and phone[0] != '8':
                    self.__ERROR_LOG.write(f"Attempt to set phone from another country ({phone}): "
                                           f"{self.__get_username()}")
                    raise ValueError('Wrong phone country')
                phone = phone[1:]
            elif len(phone) != 10:
                self.__ERROR_LOG.write(f"Attempt to set invalid phone ({phone}): {self.__get_username()}")
                raise ValueError('Wrong phone number')
            return phone

    def _get_correct_document_type(self, document_type):
        if self._check_if_is_str(document_type):
            document_type = document_type.lower()
            if document_type not in self.__document_types:
                self.__ERROR_LOG.write(f"Attempt to set invalid document type({document_type}): "
                                       f"{self.__get_username()}")
                raise ValueError('Wrong document type')
            return document_type

    def _get_correct_document_id(self, document_id):
        if self._check_if_is_str(document_id):
            document_id = re.findall(r'\d+', document_id)
            document_id = ''.join(document_id)
            if len(document_id) != self.__document_types[self.__document_type]:
                self.__ERROR_LOG.write(f"Attempt to set invalid document id ({document_id}): {self.__get_username()}")
                raise ValueError('Wrong number of digits in document id')
            return document_id

    @classmethod
    def create(cls, first_name, last_name, birth_date, phone, document_type, document_id):
        return Patient(first_name, last_name, birth_date, phone, document_type, document_id)

    def save(self):
        data = pd.DataFrame([[self.first_name, self.last_name, self.birth_date,
                              self.phone, self.document_type, self.document_id]])
        data.to_csv('patients.csv', mode='a', header=False, index=False)
        self.__INFO_LOG.write(f"Saving to csv-file: {self.__get_username()}")


class PatientCollectionIterator:
    def __init__(self, path_to_file, limit=None):
        self.__path_to_file = path_to_file
        self.__index = 0
        self.__limit = limit

    def __iter__(self):
        return self

    def __next__(self):
        if os.path.getsize(self.__path_to_file) == 0:
            raise StopIteration
        file_len = len(pd.read_csv(self.__path_to_file, header=None))
        if self.__limit is None:
            end = file_len
        else:
            if self.__limit > len(pd.read_csv(self.__path_to_file, header=None)):
                end = file_len
            else:
                end = self.__limit
        if self.__index < end:
            self.__index += 1
            patient_info = pd.read_csv(self.__path_to_file, nrows=self.__index, dtype=str,
                                       skiprows=self.__index - 1, header=None).iloc[0].tolist()
            return Patient(*patient_info)
        else:
            raise StopIteration


class PatientCollection:

    def __init__(self, path_to_file):
        if not os.path.isfile(path_to_file):
            raise FileNotFoundError(f'Not exist: {path_to_file}')
        self.path_to_file = path_to_file

    def __iter__(self):
        return PatientCollectionIterator(self.path_to_file)

    def limit(self, n):
        return PatientCollectionIterator(self.path_to_file, n)
