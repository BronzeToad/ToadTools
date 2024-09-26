from typing import Type, List, Tuple, Any

from pydantic import BaseModel


class PydanticModelPrinter:
    """
    Utility class for printing Pydantic model instances with colored output.

    Color codes:
        - RED: Required fields
        - YELLOW: Optional fields
        - GREEN: Computed fields
    """

    RED = "\033[91m"  # Required fields color code
    YELLOW = "\033[93m"  # Optional fields color code
    GREEN = "\033[92m"  # Computed fields color code
    RESET = "\033[0m"  # Reset color code

    @classmethod
    def get_model_details(cls, model_instance: BaseModel) -> str:
        """Return the formatted details of a Pydantic model instance.

        Args:
            model_instance (BaseModel): The Pydantic model instance.

        Returns:
            str: The formatted model details.
        """
        model_class: Type[BaseModel] = model_instance.__class__
        model_name: str = model_class.__name__
        output_lines: List[str] = [f"Model: {model_name}"]

        required_fields: List[str] = cls._get_required_fields(model_class)
        optional_fields: List[str] = cls._get_optional_fields(model_class)
        computed_fields: List[str] = cls._get_computed_fields(model_class)

        # Combine all fields into a single list with their corresponding color
        all_fields: List[Tuple[str, Any, str]] = []

        # Required fields
        for field_name in required_fields:
            value: Any = getattr(model_instance, field_name)
            all_fields.append((field_name, value, cls.RED))

        # Optional fields
        for field_name in optional_fields:
            value: Any = getattr(model_instance, field_name)
            all_fields.append((field_name, value, cls.YELLOW))

        # Computed fields
        for field_name in computed_fields:
            value: Any = getattr(model_instance, field_name)
            all_fields.append((field_name, value, cls.GREEN))

        # Build the output lines
        for field_name, value, color in all_fields:
            output_lines.append(f"  {color}{field_name}: {value}{cls.RESET}")

        # Join all lines into a single string
        return "\n".join(output_lines)

    @classmethod
    def _get_required_fields(cls, model_class: Type[BaseModel]) -> List[str]:
        """Get a list of required field names from a Pydantic model class.

        Args:
            model_class (Type[BaseModel]): The Pydantic model class.

        Returns:
            List[str]: A list of required field names.
        """
        return [
            field_name
            for field_name, field in model_class.model_fields.items()
            if field.is_required()
        ]

    @classmethod
    def _get_optional_fields(cls, model_class: Type[BaseModel]) -> List[str]:
        """Get a list of optional field names from a Pydantic model class.

        Args:
            model_class (Type[BaseModel]): The Pydantic model class.

        Returns:
            List[str]: A list of optional field names.
        """
        return [
            field_name
            for field_name, field in model_class.model_fields.items()
            if not field.is_required()
        ]

    @classmethod
    def _get_computed_fields(cls, model_class: Type[BaseModel]) -> List[str]:
        """Get a list of computed field names (properties) defined in the model class.

        Args:
            model_class (Type[BaseModel]): The Pydantic model class.

        Returns:
            List[str]: A list of computed field names.
        """
        return [
            name
            for name, value in vars(model_class).items()
            if isinstance(value, property) and not name.startswith("_")
        ]


class PrintableBaseModel(BaseModel):
    """BaseModel with a custom string representation using PydanticModelPrinter."""

    def __str__(self) -> str:
        """Return the string representation of the model instance.

        Returns:
            str: The formatted model details.
        """
        return PydanticModelPrinter.get_model_details(self)


if __name__ == "__main__":
    # Example usage
    class User(PrintableBaseModel):
        id: int
        name: str = "Unknown"
        age: int = None

        @property
        def is_adult(self) -> bool:
            return self.age >= 18 if self.age is not None else False

    user = User(id=1)
    print(user)
