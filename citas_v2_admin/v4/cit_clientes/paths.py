"""
Cit Clientes v4, rutas (paths)
"""
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from lib.database import Session, get_db
from lib.exceptions import MyAnyError
from lib.fastapi_pagination_custom_page import CustomPage

from ...core.permisos.models import Permiso
from ..usuarios.authentications import UsuarioInDB, get_current_active_user
from .crud import get_cit_cliente, get_cit_clientes
from .schemas import CitClienteOut, OneCitClienteOut

cit_clientes = APIRouter(prefix="/v4/cit_clientes", tags=["categoria"])


@cit_clientes.get("", response_model=CustomPage[CitClienteOut])
async def paginado_cit_clientes(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    apellido_primero: str = None,
    apellido_segundo: str = None,
    autoriza_mensajes: bool = None,
    creado: date = None,
    creado_desde: date = None,
    creado_hasta: date = None,
    curp: str = None,
    email: str = None,
    enviar_boletin: bool = None,
    nombres: str = None,
    telefono: str = None,
    tiene_contrasena_sha256: bool = None,
):
    """Paginado de clientes"""
    if current_user.permissions.get("CIT CLIENTES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        resultados = get_cit_clientes(
            database=database,
            apellido_primero=apellido_primero,
            apellido_segundo=apellido_segundo,
            autoriza_mensajes=autoriza_mensajes,
            creado=creado,
            creado_desde=creado_desde,
            creado_hasta=creado_hasta,
            curp=curp,
            email=email,
            enviar_boletin=enviar_boletin,
            nombres=nombres,
            telefono=telefono,
            tiene_contrasena_sha256=tiene_contrasena_sha256,
        )
    except MyAnyError as error:
        return CustomPage(success=False, message=str(error))
    return paginate(resultados)


@cit_clientes.get("/{cit_cliente_id}", response_model=OneCitClienteOut)
async def detalle_cit_cliente(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    cit_cliente_id: int,
):
    """Detalle de un cliente a partir de su id"""
    if current_user.permissions.get("CIT CLIENTES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        cit_cliente = get_cit_cliente(database, cit_cliente_id)
    except MyAnyError as error:
        return OneCitClienteOut(success=False, message=str(error))
    return OneCitClienteOut.model_validate(cit_cliente)
