from collections import UserDict
from datetime import datetime, timedelta
import pickle
from abc import ABC, abstractmethod


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()
    
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and 10 numbers phone please."
        except IndexError:
            return "Enter the argument for the command"
        except KeyError:
            return "Enter correct user name"
           
    return inner

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not self.validate_phone(value):
            raise ValueError("The phone number must contain 10 digits")
        super().__init__(value)

    @staticmethod
    def validate_phone(value):
        return len(value) == 10 and value.isdigit()
    

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, '%d.%m.%Y').date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
    def __str__(self):
        return self.value.strftime('%d.%m.%Y')


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def delete_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                break

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                break

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p.value
            
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(str(p) for p in self.phones)}, birthday: {self.birthday}"


class AddressBook:
    def __init__(self):
        self.data = {}

    def add_record(self, record):
        self.data[record.name.value] = record

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def find(self, name):
        return self.data.get(name)
    
    def get_upcoming_birthdays(self):
        days = 7
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                if 0 <= (birthday_this_year - today).days <= days:
                    if birthday_this_year.weekday() >= 5:
                        birthday_this_year = self.find_next_weekday(birthday_this_year, 0)

                    congratulation_date_str = birthday_this_year.strftime('%d.%m.%Y')
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date": congratulation_date_str
                    })
        return upcoming_birthdays

    @staticmethod
    def find_next_weekday(d: datetime, weekday: int):
        next_days = weekday - d.weekday()
        if next_days <= 0:
            next_days += 7
        return d + timedelta(days=next_days)


class AbstractAssistant(ABC):
    @abstractmethod
    def handle(self, args, book:AddressBook):
        pass


class AddContactAssistant(AbstractAssistant):
    @input_error
    def handle(self, args, book: AddressBook):
        name, phone, *_ = args
        record = book.find(name)
        message = "Contact updated."
        if record is None:
            record = Record(name)
            book.add_record(record)
            message = "Contact added."
        if phone:
            record.add_phone(phone)
        return message


class ChangeContactAssistant(AbstractAssistant):
    @input_error
    def handle(self, args, book: AddressBook):
        name, new_phone, *_ = args
        record = book.find(name)
        if record:
            if new_phone:
                record.edit_phone(record.phones[0].value, new_phone)
                return "Contact updated."
            else:
                raise ValueError("Enter the new phone number")
        else:
            raise KeyError("Enter correct user name")
        

class ShowPhoneAssistant(AbstractAssistant):
    @input_error
    def handle(self, args, book: AddressBook):
        name = args[0]
        record = book.find(name)
        if record:
            return f"{name}`s phone {record.phones[0]}"
        else:
            return "Contact not found."
        

class ShowAllAssistant(AbstractAssistant):
    @input_error
    def handle(self, book: AddressBook):
        return [str(record) for record in book.data.values()]
    

class AddBirthdayAssistant(AbstractAssistant):
    @input_error
    def handle(self, args, book: AddressBook):
        name, *_, birthday = args
        record = book.find(name)
        message = "Birthday added."
        if record is None:
            message = "Contact not found."
        if record:
            record.add_birthday(birthday)
        return message
    

class ShowBirthdayAssistant(AbstractAssistant):
    @input_error
    def handle(self, args, book: AddressBook):
        name = args[0]
        record = book.find(name)
        if record:
            return f"{name}`s birthday {record.birthday}"
        else:
            return "Contact not found."
        

class BirthdaysAssistant(AbstractAssistant):    
    @input_error
    def handle(self, args, book: AddressBook):
        get_upcoming_birthdays = book.get_upcoming_birthdays()
        if get_upcoming_birthdays:
            return get_upcoming_birthdays
        else:
            return "No upcoming birthdays"


class ShowHelpAssistant(AbstractAssistant):        
    @input_error
    def handle(self):
        commands = [
            "help - Show all commands",
            "add - Add a new contact",
            "change - Change contact information",
            "phone - Show contact's phone number",
            "all - Show all contacts",
            "add-birthday - Add birthday to a contact",
            "show-birthday - Show contact's birthday",
            "birthdays - Show upcoming birthdays",
            "exit, close - Exit the program"
        ]
        return commands
        

class AssistantForCustomer:
    def __init__(self):
        self.book = load_data()
        self.assistant = {
            "add": AddContactAssistant(),
            "change": ChangeContactAssistant(),
            "phone": ShowPhoneAssistant(),
            "all": ShowAllAssistant(),
            "add-birthday": AddBirthdayAssistant(),
            "show-birthday": ShowBirthdayAssistant(),
            "birthdays": BirthdaysAssistant(),
            "help": ShowHelpAssistant()
        }

    @staticmethod
    @input_error
    def parse_input(user_input):
        cmd, *args = user_input.split()
        cmd = cmd.strip().lower()
        return cmd, args

    def run(self):
        print("Welcome to the assistant bot!")
        while True:
            user_input = input("Enter a command: ")
            try:
                command, args = self.parse_input(user_input)
                if command == "close" or command == "exit":
                    print("Good bye!")
                    break
                elif command == "help":
                    print("\n".join(self.assistant[command].handle()))                
                elif command == "all":
                    print("\n".join(self.assistant[command].handle(self.book)))
                elif command in self.assistant:
                    result = self.assistant[command].handle(args, self.book)
                    if isinstance(result, list):
                        for item in result:
                            print(item)
                    else:
                        print(result)
                elif command == "hello":
                    print("How can I help you?")
                else:
                    print("Invalid command. Type 'help' for available commands.")
            except Exception as e:
                print(e)
                
        save_data(self.book)

if __name__ == "__main__":
    assistant = AssistantForCustomer()
    assistant.run()