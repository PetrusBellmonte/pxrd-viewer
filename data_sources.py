from dataclasses import dataclass
from pathlib import Path
import random
import numpy as np


@dataclass
class Spectrum:
    """
    Represents a measured spectrum.
    """

    name: str
    source_file: Path
    contained_elements: list[str]

    def _load_data(self):
        """
        Loads the spectrum data from the source file.
        """
        data = np.loadtxt(self.source_file)
        if data.shape[1] != 2:
            raise ValueError(
                f"File {self.source_file} does not contain exactly two columns."
            )
        self._x, self._y = data[:, 0], data[:, 1]
        self._y = self._y / np.max(self._y)  # Normalize intensity

    @property
    def x(self):
        if not hasattr(self, "_x"):
            self._load_data()
        return self._x

    @property
    def y(self):
        if not hasattr(self, "_y"):
            self._load_data()
        return self._y


ALL_ELEMENTS = [
    "H",
    "He",
    "Li",
    "Be",
    "B",
    "C",
    "N",
    "O",
    "F",
    "Ne",
    "Na",
    "Mg",
    "Al",
    "Si",
    "P",
    "S",
    "Cl",
    "Ar",
    "K",
    "Ca",
    "Sc",
    "Ti",
    "V",
    "Cr",
    "Mn",
    "Fe",
    "Co",
    "Ni",
    "Cu",
    "Zn",
    "Ga",
    "Ge",
    "As",
    "Se",
    "Br",
    "Kr",
    "Rb",
    "Sr",
    "Y",
    "Zr",
    "Nb",
    "Mo",
    "Tc",
    "Ru",
    "Rh",
    "Pd",
    "Ag",
    "Cd",
    "In",
    "Sn",
    "Sb",
    "Te",
    "I",
    "Xe",
    "Cs",
    "Ba",
    "La",
    "Ce",
    "Pr",
    "Nd",
    "Pm",
    "Sm",
    "Eu",
    "Gd",
    "Tb",
    "Dy",
    "Ho",
    "Er",
    "Tm",
    "Yb",
    "Lu",
    "Hf",
    "Ta",
    "W",
    "Re",
    "Os",
    "Ir",
    "Pt",
    "Au",
    "Hg",
    "Tl",
    "Pb",
    "Bi",
    "Po",
    "At",
    "Rn",
    "Fr",
    "Ra",
    "Ac",
    "Th",
    "Pa",
    "U",
    "Np",
    "Pu",
    "Am",
    "Cm",
    "Bk",
    "Cf",
    "Es",
    "Fm",
    "Md",
    "No",
    "Lr",
    "Rf",
    "Db",
    "Sg",
    "Bh",
    "Hs",
    "Mt",
    "Ds",
    "Rg",
    "Cn",
    "Nh",
    "Fl",
    "Mc",
    "Lv",
    "Ts",
    "Og",
]


def list_available_spectra() -> list[Spectrum]:
    """
    Lists all available spectra.

    Returns:
        list[Spectrum]: A list of Spectrum objects representing available spectra.
    """
    # This function should return a list of Spectrum objects.
    # For demonstration purposes, we return an empty list.
    data_dir = Path(__file__).parent / "data"
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory {data_dir} does not exist.")
    spectra = []
    for file in data_dir.glob("*.xyd"):
        rs = random.Random(file.stem)
        contained_elements = rs.sample(ALL_ELEMENTS, k=rs.randint(1, 5))
        spectra.append(
            Spectrum(
                name=file.stem, source_file=file, contained_elements=contained_elements
            )
        )
    return spectra
