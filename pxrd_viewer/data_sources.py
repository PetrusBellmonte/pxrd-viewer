from pathlib import Path
import struct
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
        description: str = "",
        display_name: str = None,
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
        self.description = description
        self.display_name = display_name

    @staticmethod
    def from_meta(meta: dict, meta_file: Path) -> "Spectrum":
        """
        Create a Spectrum instance from meta dictionary and meta file path.
        """
        name = meta.get("name")
        contained_elements = set(meta.get("contained_elements", []))
        tags = meta.get("tags", [])
        description = meta.get("description", "")
        display_name = meta.get("display_name", None)
        source_file = meta_file.parent / meta.get("source_file")
        return Spectrum(
            name=name,
            source_file=source_file,
            contained_elements=contained_elements,
            tags=tags,
            description=description,
            display_name=display_name,
        )

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

    @property
    def readable_name(self):
        return self.display_name if self.display_name else self.name


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

def read_raw_file(data_source: io.BytesIO) -> dict:
    data = data_source.read()
    def read_str(offset, length):
        return data[offset:offset+length].decode("ascii", errors="ignore").rstrip("\x00")

    def read_u16(offset):
        return struct.unpack_from("<H", data, offset)[0]

    def read_u32(offset):
        return struct.unpack_from("<I", data, offset)[0]

    def read_s16_array(offset, count):
        return struct.unpack_from(f"<{count}h", data, offset)
    
    def read_s32_array(offset, count):
        return struct.unpack_from(f"<{count}i", data, offset)

    def read_float(offset):
        return struct.unpack_from("<f", data, offset)[0]

    # Extract values
    result = {
        "format": read_str(0x00, 8),
        "machine": read_str(0x08, 8),
        "date": read_str(0x10, 0x10),
        "title": read_str(0x20, 0x20),
        "comment": read_str(0x70, 0x20),
        "kilo_volt": read_u16(0x13E),
        "milli_Amp": read_u16(0x140),
        "radiation": read_float(0x142),
        "radiation_false": read_float(0x146),
    }


    if not result['machine']in ['POLY II', 'Powdat']:
        raise ValueError(f"Unsupported machine type. Got {result['machine']}, expected 'POLY II' or 'Powdat'.")
    # DataInfo struct at 0x600 for POLY II, 0x800 for Powdat
    info_offset = 0x600 if result['machine'] == 'POLY II' else 0x800
    result["collection_start_date"] = read_str(info_offset, 0x10)
    result["collection_end_date"] = read_str(info_offset+0x10, 0x10)
    result["num_points"] = read_u16(info_offset+0x22)
    result["theta_start"] = read_float(info_offset+0x2C) 
    result["theta_end"] = read_float(info_offset+0x34)
    result["theta_stepsize"] = read_float(info_offset+0x3C)
    result["time_per_step"] = read_float(info_offset+0x44)
    result["min_cnt"] = read_u32(info_offset+0x78)
    result["max_cnt"] = read_u32(info_offset+0x7C)

    data_offset = info_offset + 0x200
    if result['machine'] == 'POLY II':
        result["data"] = read_s16_array(data_offset, result["num_points"])
    elif result['machine'] == 'Powdat':
        result["data"] = read_s32_array(data_offset, result["num_points"])
    return result

def raw_info_to_normalized_numpy(info):
    x = np.linspace(info["theta_start"], info["theta_end"], info["num_points"])
    x = (4 * np.pi / info["radiation"]) * np.sin(np.radians(x) / 2)  # Convert to Q
    y = np.array(info["data"], dtype=np.float32)
    y /= np.max(y)  # Normalize to max of 1.0
    return x, y

def load_raw_file(uploaded_file: io.BytesIO) -> tuple[np.ndarray, np.ndarray]:
    info = read_raw_file(uploaded_file)
    x, y = raw_info_to_normalized_numpy(info)
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
        spectrum = Spectrum.from_meta(meta, meta_file)
        spectra.append(spectrum)
    return spectra


def save_new_spectrum(
    name: str,
    uploaded_file: io.BytesIO,
    contained_elements: set[str],
    tags: list[str],
    description: str = "",
    display_name: str = None,
) -> Spectrum:
    source_file = DATA_DIR / f"{name}.npz"
    if source_file.exists():
        raise FileExistsError(f"Spectrum with name '{name}' already exists.")
    x, y = uploaded_file
    np.savez_compressed(source_file, x=x, y=y)
    meta_file = DATA_DIR / f"{name}.meta"
    meta_data = {
        "name": name,
        "source_file": source_file.name,
        "contained_elements": list(contained_elements),
        "tags": tags,
        "description": description,
        "display_name": display_name,
    }
    with open(meta_file, "w") as f:
        yaml.dump(meta_data, f)
    list_available_spectra.cache_clear()
    return Spectrum(
        name=name,
        source_file=source_file,
        contained_elements=contained_elements,
        tags=tags,
        description=description,
        display_name=display_name,
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


def edit_spectrum(
    old_spectrum: Spectrum,
    new_name: str = None,
    contained_elements: set[str] = None,
    tags: list[str] = None,
    description: str = None,
    display_name: str = None,
) -> Spectrum:
    """
    Edits the metadata of an existing spectrum.

    Args:
        old_spectrum (Spectrum): The Spectrum object to edit.
        new_name (str, optional): The new name for the spectrum.
        contained_elements (set[str], optional): New set of contained elements.
        tags (list[str], optional): New list of tags.

    Returns:
        Spectrum: The updated Spectrum object.
    """
    meta_file = DATA_DIR / f"{old_spectrum.name}.meta"
    if not meta_file.exists():
        raise FileNotFoundError(f"Spectrum '{old_spectrum.name}' does not exist.")

    updated_name = new_name if new_name is not None else old_spectrum.name
    updated_elements = (
        contained_elements
        if contained_elements is not None
        else old_spectrum.contained_elements
    )
    updated_tags = tags if tags is not None else old_spectrum.tags
    updated_description = (
        description
        if description is not None
        else getattr(old_spectrum, "description", "")
    )
    updated_display_name = (
        display_name
        if display_name is not None
        else getattr(old_spectrum, "display_name", None)
    )
    source_file = old_spectrum.source_file

    # If renaming, update file names
    if new_name and new_name != old_spectrum.name:
        new_source_file = DATA_DIR / f"{new_name}.npz"
        new_meta_file = DATA_DIR / f"{new_name}.meta"
        if new_source_file.exists() or new_meta_file.exists():
            raise FileExistsError(f"Spectrum with name '{new_name}' already exists.")
        source_file.rename(new_source_file)
        meta_file.rename(new_meta_file)
        source_file = new_source_file
        meta_file = new_meta_file

    meta_data = {
        "name": updated_name,
        "source_file": source_file.name,
        "contained_elements": list(updated_elements),
        "tags": updated_tags,
        "description": updated_description,
        "display_name": updated_display_name,
    }
    with open(meta_file, "w") as f:
        yaml.dump(meta_data, f)

    list_available_spectra.cache_clear()
    return Spectrum(
        name=updated_name,
        source_file=source_file,
        contained_elements=set(updated_elements),
        tags=updated_tags,
        description=updated_description,
        display_name=updated_display_name,
    )


def list_used_tags() -> set[str]:
    tags = set()
    for spectrum in list_available_spectra():
        tags.update(spectrum.tags)
    return tags
