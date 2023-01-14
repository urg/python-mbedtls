# SPDX-License-Identifier: MIT
# Copyright (c) 2022, Mathias Laurin

from __future__ import annotations

import enum
import numbers
import os
import sys
from typing import (
    Callable,
    NamedTuple,
    NoReturn,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
    overload,
)

if sys.version_info < (3, 8):
    from typing_extensions import Final, Literal
else:
    from typing import Final, Literal

if sys.version_info < (3, 9):
    _PathLike = os.PathLike
else:
    _PathLike = os.PathLike[str]

_Path = Union[_PathLike, str]
CIPHER_NAME: Final[Sequence[bytes]] = ...
_DER = bytes
_PEM = str
_NUM = int
_MPI = Union[numbers.Integral, int]

class CipherType(enum.Enum):
    NONE: int
    RSA: int
    ECKEY: int
    ECKEY_DH: int
    ECDSA: int
    RSA_ALT: int
    RSASSA_PSS: int

class KeyPair(NamedTuple):
    private: Union[_DER, _PEM]
    public: Union[_DER, _PEM]

class Curve(bytes, enum.Enum):
    SECP192R1: bytes
    SECP224R1: bytes
    SECP256R1: bytes
    SECP384R1: bytes
    SECP521R1: bytes
    BRAINPOOLP256R1: bytes
    BRAINPOOLP384R1: bytes
    BRAINPOOLP512R1: bytes
    SECP192K1: bytes
    SECP224K1: bytes
    SECP256K1: bytes
    CURVE25519: bytes
    CURVE448: bytes

def check_pair(pub: CipherBase, priv: CipherBase) -> bool: ...
def get_supported_ciphers() -> Sequence[bytes]: ...
def get_supported_curves() -> Sequence[Curve]: ...

# `Self` (PEP 673) should work as well but did not with typing_extensions 4.2.0
_TCipherBase = TypeVar("_TCipherBase", bound=CipherBase)

class CipherBase:
    def __init__(
        self,
        name: bytes,
        key: Optional[bytes] = ...,
        password: Optional[bytes] = ...,
    ) -> None: ...
    def __hash__(self) -> int: ...
    def __eq__(self, other: object) -> bool: ...
    @classmethod
    def from_buffer(
        cls: Type[_TCipherBase],
        buffer: bytes,
        password: Optional[
            Union[Callable[[], Union[bytes, bytearray]], bytes, bytearray]
        ] = None,
    ) -> _TCipherBase: ...
    @classmethod
    def from_file(
        cls: Type[_TCipherBase],
        path: _Path,
        password: Optional[
            Union[Callable[[], Union[bytes, bytearray]], bytes, bytearray]
        ] = None,
    ) -> _TCipherBase: ...
    @classmethod
    def from_DER(cls: Type[_TCipherBase], key: bytes) -> _TCipherBase: ...
    @classmethod
    def from_PEM(cls: Type[_TCipherBase], key: str) -> _TCipherBase: ...
    @property
    def name(self) -> bytes: ...
    @property
    def key_size(self) -> int: ...
    def _has_private(self) -> bool: ...
    def _has_public(self) -> bool: ...
    def sign(
        self, message: bytes, digestmod: Optional[str] = ...
    ) -> bytes: ...
    def verify(
        self, message: bytes, signature: bytes, digestmod: str
    ) -> bool: ...
    def encrypt(self, message: bytes) -> bytes: ...
    def decrypt(self, message: bytes) -> bytes: ...
    def to_PEM(self) -> KeyPair: ...
    def __str__(self) -> _PEM: ...
    def to_DER(self) -> KeyPair: ...
    def to_bytes(self) -> _DER: ...
    def __bytes__(self) -> _DER: ...

class RSA(CipherBase):
    def __init__(
        self, key: Optional[bytes] = ..., password: Optional[bytes] = ...
    ) -> None: ...
    def generate(self, key_size: int = ..., exponent: int = ...) -> _DER: ...
    @overload
    def export_key(self, format: Literal["DER"]) -> _DER: ...
    @overload
    def export_key(self, format: Literal["PEM"]) -> _PEM: ...
    @overload
    def export_key(self) -> Union[_DER, _PEM]: ...
    @overload
    def export_public_key(self, format: Literal["DER"]) -> _DER: ...
    @overload
    def export_public_key(self, format: Literal["PEM"]) -> _PEM: ...
    @overload
    def export_public_key(self) -> Union[_DER, _PEM]: ...

class ECPoint:
    def __init__(self, x: _MPI, y: _MPI, z: _MPI) -> None: ...
    @property
    def x(self) -> _MPI: ...
    @property
    def y(self) -> _MPI: ...
    @property
    def z(self) -> _MPI: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __bool__(self) -> bool: ...

class ECC(CipherBase):
    def __init__(
        self,
        curve: Optional[Curve] = ...,
        key: Optional[bytes] = ...,
        password: Optional[bytes] = ...,
    ) -> None: ...
    @property
    def curve(self) -> Curve: ...
    def generate(self) -> bytes: ...
    @overload
    def export_key(self, format: Literal["DER"]) -> _DER: ...
    @overload
    def export_key(self, format: Literal["PEM"]) -> _PEM: ...
    @overload
    def export_key(self, format: Literal["NUM"]) -> _NUM: ...
    @overload
    def export_key(self) -> Union[_DER, _PEM, _NUM]: ...
    @overload
    def export_public_key(self, format: Literal["DER"]) -> _DER: ...
    @overload
    def export_public_key(self, format: Literal["PEM"]) -> _PEM: ...
    @overload
    def export_public_key(self, format: Literal["POINT"]) -> ECPoint: ...
    @overload
    def export_public_key(self) -> Union[_DER, _PEM, ECPoint]: ...

class DHServer:
    def __init__(self, modulus: _MPI, generator: _MPI) -> None: ...
    def __getstate__(self) -> NoReturn: ...
    @property
    def key_size(self) -> int: ...
    @property
    def modulus(self) -> _MPI: ...
    @property
    def generator(self) -> _MPI: ...
    @property
    def _secret(self) -> _MPI: ...
    @property
    def shared_secret(self) -> _MPI: ...
    def generate_secret(self) -> _MPI: ...
    def generate(self) -> bytes: ...
    def import_CKE(self, buffer: bytes) -> None: ...

class DHClient:
    def __init__(self, modulus: _MPI, generator: _MPI) -> None: ...
    def __getstate__(self) -> NoReturn: ...
    @property
    def key_size(self) -> int: ...
    @property
    def modulus(self) -> _MPI: ...
    @property
    def generator(self) -> _MPI: ...
    @property
    def _secret(self) -> _MPI: ...
    @property
    def shared_secret(self) -> _MPI: ...
    def generate_secret(self) -> _MPI: ...
    def generate(self) -> bytes: ...
    def import_SKE(self, buffer: bytes) -> None: ...

class ECDHClient:
    private_key: _MPI
    public_key: ECPoint
    peers_public_key: ECPoint
    def __init__(self, ecc: ECC) -> None: ...
    def __getstate__(self) -> NoReturn: ...
    def _has_private(self) -> bool: ...
    def _has_public(self) -> bool: ...
    def _has_peers_public(self) -> bool: ...
    @property
    def shared_secret(self) -> _MPI: ...
    def generate_secret(self) -> _MPI: ...
    def generate_public_key(self) -> None: ...
    def generate(self) -> bytes: ...
    def import_SKE(self, buffer: bytes) -> None: ...

class ECDHServer:
    private_key: _MPI
    public_key: ECPoint
    peers_public_key: ECPoint
    def __init__(self, ecc: ECC) -> None: ...
    def __getstate__(self) -> NoReturn: ...
    def _has_private(self) -> bool: ...
    def _has_public(self) -> bool: ...
    def _has_peers_public(self) -> bool: ...
    @property
    def shared_secret(self) -> _MPI: ...
    def generate_secret(self) -> _MPI: ...
    def generate_public_key(self) -> None: ...
    def generate(self) -> bytes: ...
    def import_CKE(self, buffer: bytes) -> None: ...

class ECDHNaive:
    private_key: _MPI
    public_key: ECPoint
    peers_public_key: ECPoint
    def __init__(self, curve: Optional[Curve] = ...) -> None: ...
    def __getstate__(self) -> NoReturn: ...
    def _has_private(self) -> bool: ...
    def _has_public(self) -> bool: ...
    def _has_peers_public(self) -> bool: ...
    @property
    def shared_secret(self) -> _MPI: ...
    def generate_secret(self) -> _MPI: ...
    def generate_public_key(self) -> None: ...
    def generate(self) -> ECPoint: ...
    def import_SKE(self, buffer: bytes) -> None: ...
    # extra methods
    def import_peer_public(self, pubkey: ECPoint) -> None: ...
    def import_peers_public(self, pubkey: ECPoint) -> None: ...
