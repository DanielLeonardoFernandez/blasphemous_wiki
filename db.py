from sqlmodel import SQLModel, create_engine, Session, select
from contextlib import asynccontextmanager

DATABASE_URL = "sqlite:///./blasphemous.db"
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

@asynccontextmanager
async def create_tables(app):
    # crea tablas
    SQLModel.metadata.create_all(engine)

    # seed inicial (solo si no hay categorias)
    from models import Categoria, Ubicacion, Interaccion, Item, ItemLocationLink, ItemInteraccionLink

    with Session(engine) as session:
        existe = session.exec(select(Categoria)).first()
        if not existe:
            # categorias de ejemplo
            cat_names = [
                ("Rosario", "Objetos tipo rosario"),
                ("Reliquia", "Reliquias importantes"),
                ("Consumible", "Consumibles"),
                ("Mea Culpa", "Mea Culpa / objetos clave")
            ]
            categorias = [Categoria(nombre=n, descripcion=d) for n, d in cat_names]
            session.add_all(categorias)
            session.commit()

            # ubicaciones de ejemplo
            locs = [
                Ubicacion(nombre="Iglesia de los Caídos", tipo="area", descripcion="Área inicial"),
                Ubicacion(nombre="Tienda del Comerciante", tipo="tienda", descripcion="Vendedor del juego"),
                Ubicacion(nombre="Mazmorra Profunda", tipo="mazmorra", descripcion="Lugar secreto")
            ]
            session.add_all(locs)
            session.commit()

            # interacciones de ejemplo
            inters = [
                Interaccion(descripcion="Entregar reliquia X"),
                Interaccion(descripcion="Resolver puzzle de la estatua"),
            ]
            session.add_all(inters)
            session.commit()

            # items de ejemplo (asocia por ids)
            # recupera ids
            cat_map = {c.nombre: c for c in session.exec(select(Categoria)).all()}
            loc_map = {l.nombre: l for l in session.exec(select(Ubicacion)).all()}
            inter_map = {i.descripcion: i for i in session.exec(select(Interaccion)).all()}

            item1 = Item(
                nombre="Rosario de Agujas",
                descripcion="Aumenta ataque",
                costo=100,
                indispensable=False,
                categoria_id=cat_map["Rosario"].id
            )
            session.add(item1)
            session.commit()
            session.refresh(item1)
            # link ubicacion
            session.add(ItemLocationLink(item_id=item1.id, ubicacion_id=loc_map["Iglesia de los Caídos"].id))
            session.commit()

            item2 = Item(
                nombre="Reliquia de la Lengua",
                descripcion="Objeto clave para final",
                costo=None,
                indispensable=True,
                categoria_id=cat_map["Reliquia"].id
            )
            session.add(item2)
            session.commit()
            session.refresh(item2)
            # links
            session.add(ItemLocationLink(item_id=item2.id, ubicacion_id=loc_map["Mazmorra Profunda"].id))
            # interacción requerida
            session.add(ItemInteraccionLink(item_id=item2.id, interaccion_id=inter_map["Entregar reliquia X"].id))
            session.commit()

    yield
