from pathlib import Path
import numpy as np
import io
import yaml
import functools

DATA_DIR = Path(__file__).parent / "spectra"
DATA_DIR.mkdir(exist_ok=True)


class Spectrum:
    """
    Represents a measured spectrum.
    """

    def __init__(
        self,
        name: str,
        source_file: Path | str,
        contained_elements: set[str] = None,
        tags: list[str] = None,
    ):
        self.name = name
        self.source_file = source_file
        if isinstance(self.source_file, str):
            self.source_file = Path(self.source_file)
        if not self.source_file.exists():
            raise FileNotFoundError(f"Source file {self.source_file} does not exist.")

        self.contained_elements = (
            contained_elements if contained_elements is not None else {}
        )
        self.tags = tags if tags is not None else []

    def _load_data(self):
        """
        Loads the spectrum data from the source file.
        """
        data = np.load(self.source_file)
        self._x = data["x"]
        self._y = data["y"]

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

    def __eq__(self, value):
        if not isinstance(value, Spectrum):
            return False
        return self.name == value.name and self.source_file == value.source_file


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


def load_xyd_file(uploaded_file: io.BytesIO) -> tuple[np.ndarray, np.ndarray]:
    data = np.loadtxt(uploaded_file)
    if data.shape[1] != 2:
        raise ValueError("Uploaded file does not contain exactly two columns.")
    x, y = data[:, 0], data[:, 1]
    y = y / np.max(y)  # Normalize intensity
    return x, y


@functools.cache
def list_available_spectra() -> list[Spectrum]:
    """
    Lists all available spectra.

    Returns:
        list[Spectrum]: A list of Spectrum objects representing available spectra.
    """
    spectra = []
    for meta_file in DATA_DIR.glob("*.meta"):
        with open(meta_file, "r") as f:
            meta = yaml.safe_load(f)
        assert "name" in meta, f"Meta file {meta_file} is missing 'name' field."
        assert "source_file" in meta, (
            f"Meta file {meta_file} is missing 'source_file' field."
        )
        name = meta.get("name")
        contained_elements = set(meta.get("contained_elements", []))
        tags = meta.get("tags", [])
        source_file = meta_file.parent / meta.get("source_file")
        spectrum = Spectrum(
            name=name,
            source_file=source_file,
            contained_elements=contained_elements,
            tags=tags,
        )
        spectra.append(spectrum)
    return spectra


def save_new_spectrum(
    name: str, uploaded_file: io.BytesIO, contained_elements: set[str], tags: list[str]
) -> Spectrum:
    source_file = DATA_DIR / f"{name}.npz"
    if source_file.exists():
        raise FileExistsError(f"Spectrum with name '{name}' already exists.")
    x, y = load_xyd_file(uploaded_file)
    np.savez_compressed(source_file, x=x, y=y)
    meta_file = DATA_DIR / f"{name}.meta"
    meta_data = {
        "name": name,
        "source_file": source_file.name,
        "contained_elements": list(contained_elements),
        "tags": tags,
    }
    with open(meta_file, "w") as f:
        yaml.dump(meta_data, f)
    # Invalidate cache after saving new spectrum
    list_available_spectra.cache_clear()
    return Spectrum(
        name=name,
        source_file=source_file,
        contained_elements=contained_elements,
        tags=tags,
    )

def delete_spectrum(spectrum: Spectrum) -> None:
    """
    Deletes a spectrum and its metadata by Spectrum object.

    Args:
        spectrum (Spectrum): The Spectrum object to delete.
    """
    source_file = spectrum.source_file
    meta_file = DATA_DIR / f"{spectrum.name}.meta"
    if not source_file.exists() or not meta_file.exists():
        raise FileNotFoundError(f"Spectrum '{spectrum.name}' does not exist.")
    source_file.unlink()
    meta_file.unlink()
    list_available_spectra.cache_clear()


def list_used_tags() -> set[str]:
    tags = set()
    for spectrum in list_available_spectra():
        tags.update(spectrum.tags)
    return tags
