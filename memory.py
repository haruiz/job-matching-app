from pydantic import BaseModel
import typing

class MemoryEntry(BaseModel):
    text: str

class MemorySection(BaseModel):
    name: str
    entries: typing.List[MemoryEntry]

class Memory(BaseModel):
    sections: typing.List[MemorySection] = []

    def add_entry(self, section_name: str, entry_text: str):
        for section in self.sections:
            if section.name == section_name:
                section.entries.append(MemoryEntry(text=entry_text))
                return
        self.sections.append(MemorySection(name=section_name, entries=[MemoryEntry(text=entry_text)]))

    def __str__(self):
        return "\n\n".join(
            [f"{section.name}\n\n" + "\n".join(entry.text for entry in section.entries) for section in self.sections]
        )


if __name__ == '__main__':
    memory = Memory()
    memory.add_entry("Python", "Python is a programming language.")
    memory.add_entry("Python", "Python was created by Guido van Rossum.")
    memory.add_entry("Python", "Python is easy to learn.")
    memory.add_entry("Python", "Python is versatile.")
    memory.add_entry("JavaScript", "JavaScript is a scripting language.")
    memory.add_entry("JavaScript", "JavaScript is used for web development.")
    memory.add_entry("JavaScript", "JavaScript is an interpreted language.")
    memory.add_entry("JavaScript", "JavaScript is a high-level language.")
    print(memory)