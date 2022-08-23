
import pandas as pd

path_report_oi = "./reports/oferta_individual.xlsx"
path_portafolio = "./reports/portafolio.xlsx"

#Lista de campos que se usarán del reporte estadístico de Hércules.
fields_report = [
    "Evento",
    "Documento",
    "Tipo Documento",
    "Sedes",
    "Área",
    "Ciclos",
    "Categoría Deportiva",
    "Nivel",
    "Género",
    "Categoría Precio",
    "Categoría Afiliación",
    "creada_por",
    "Estado Cotización",
    "Canal de Pago",
    "Canal de Cotización",
    "Forma de Pago",
    "Franquicias",
    "Precio Base",
    "Costo",
    "Tarifa Plena",
    "Subsidio a la Demanda",
    "Identificador del Cajero",
    "Identificador Máquina",
    "Fecha Registro",
    "Documento Titular",
    "Fecha Cotización",
    "Id Material",
    "Fecha Inicio del Servicio",
    "Fecha Fin del Servicio",
    "Id Servicio",
    "Edad",
    "Fecha de Nacimiento",
    "Valor",
    "Motivo de Cambio",
]


# Importando la data desde el reporte.
dataset=pd.read_excel(path_report_oi, usecols=fields_report)


dataset.info()


# Se eliminan todos los registros donde no haya un valor en la sede o en la fecha de reserva.
dash_dataset = dataset.dropna(subset=["Sedes", "Fecha Inicio del Servicio"])
print(
    f'Se han eliminado {dataset["Evento"].count()-dash_dataset["Evento"].count()} filas que no tienen registros para las sedes o en la fecha de reserva.'
)

# Inserción de columna "Tipo de Oferta" al final del dataset, asignádole un valor "".
dash_dataset.insert(loc=len(dash_dataset.columns), column="Tipo de Oferta", value="")

# Eliminación del prefijo "-F" en los código SAP (campo "Id Material") de la oferta FOSFEC.
dataset["Id Material"].replace(r"(\d{8})-F", r"\g<1>", inplace=True, regex=True)
dataset["Id Material"] = pd.to_numeric(dataset["Id Material"])


# Patrones empleados en el campo "Motivo de cambio" usando RegEx y con ello asignar las ofertas por Excedentes del 55% y cobro a empresas por una venta individual.
pat_exc55 = r"exc\w*\s*\d*[%]*[^excel]"
pat_empresarial = r"empr\w*\s*|conv\w*\s*|nit\s*\d*|contr|se factura"


# Asignación tipo de oferta "Pago con novedad".
dash_dataset.loc[dash_dataset["Canal de Pago"].isna(), "Tipo de Oferta"]="Pago con Novedad"

# Asignación tipo de oferta "FOSFEC".
dash_dataset.loc[dash_dataset["Evento"]=="fosfec", "Tipo de Oferta"] = "FOSFEC"

# Asignación tipo de oferta "Pago empresarial".
dash_dataset.loc[dash_dataset["Motivo de Cambio"].notna() & dash_dataset["Motivo de Cambio"].str.contains(pat_empresarial, case=False, regex=True), "Tipo de Oferta"] = "Pago Empresarial"

# Asignación tipo de oferta "Excedentes del 55%".
dash_dataset.loc[(dash_dataset["Ciclos"].str.contains(pat_exc55, case=False, regex=True)) | dash_dataset["Motivo de Cambio"].str.contains(pat_exc55, case=False, regex=True), "Tipo de Oferta"] = "Excedentes del 55%"

# Asignación tipo de oferta "Venta Directa".
dash_dataset.loc[(dash_dataset["Canal de Pago"].notna()) & (dash_dataset["Motivo de Cambio"].isna()), "Tipo de Oferta"] = "Venta Directa"


fields_portafolio = [
    "UNIDAD DE NEGOCIO",
    "LINEA",
    "CODIGO SAP",
    "MATERIAL",
    "NUM. PARTICIPANTES MIN",
    "NUM. PARTICIPANTES MAX",
]


# Lista de campos del portafolio que se usarán para cruzar con el reporte estadístico.
portafolio = pd.read_excel(path_portafolio, usecols=fields_portafolio)

# Elimina las fila donde se encuentre el repetido el código SAP.
portafolio.drop_duplicates("CODIGO SAP", inplace=True, keep="first")

# Selecciona del portafolio sólo las filas donde la unidad de negocio coincida con las indicacadas en la lista "UNIDADES DE NEGOCIO", pues son las unidades que ofertan servicios en Hércules.
UNIDADES_NEGOCIO = ["EDUCACIÓN", "CULTURA", "ESPARCIMIENTO", "DESARROLLO SOCIAL"]
portafolio_hercules = portafolio[
    portafolio["UNIDAD DE NEGOCIO"].isin(UNIDADES_NEGOCIO)
]



# Se ejecuta un left-join trayendo los campos de portafolio cruzados a través del Código SAP.
dash_dataset = pd.merge(
    dash_dataset,
    portafolio_hercules[
        [
            "UNIDAD DE NEGOCIO",
            "LINEA",
            "MATERIAL",
            "CODIGO SAP",
            "NUM. PARTICIPANTES MIN",
            "NUM. PARTICIPANTES MAX",
        ]
    ],
    left_on="Id Material",
    right_on="CODIGO SAP",
    how="left",
)



dash_dataset.to_excel("dash_dataset_merged.xlsx", index = False, index_label=False)
# portafolio_hercules.to_excel("portafolio_hercules.xlsx", index=False, index_label=False)