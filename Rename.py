import enum
class myClass(enum.Enum):
    a = "12"
    b = "34"

for attr in myClass:
    print("Name / Value:", attr.name, attr.value)