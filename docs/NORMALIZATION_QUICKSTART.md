# Guía Rápida de Uso - Normalización Mejorada

## 🚀 Quick Start

### Uso Básico (Compatible con código existente)

```python
from pandas_toolkit.io.readers import CSVReader

reader = CSVReader()

# Forma tradicional - sigue funcionando
df = reader.read("data.csv", normalize=True, normalize_columns=True)
```

### Usando Presets (Nuevo - Recomendado)

```python
# Preset básico (recomendado para la mayoría de casos)
df = reader.normalize(df, preset='basic')

# Preset completo (limpieza exhaustiva)
df = reader.normalize(df, preset='full')

# Preset para análisis (reemplaza columnas originales)
df = reader.normalize(df, preset='analysis_ready')
```

## 📚 Ejemplos Prácticos

### Ejemplo 1: Limpieza de Datos de Clientes

```python
import pandas as pd
from pandas_toolkit.io.readers import CSVReader

# Datos de ejemplo
data = {
    "  Nombre  ": ["  JUAN PÉREZ  ", "  Maria García  ", "  "],
    "Email": ["juan@email.com", "MARIA@EMAIL.COM", "N/A"],
    "Teléfono": ["123-456-7890", "", "null"],
    "Status": ["ACTIVO", "activo", "Activo"]
}
df = pd.DataFrame(data)

reader = CSVReader()

# Normalización completa
df_clean = reader.normalize_columns(df)  # Normaliza nombres
df_clean = reader.normalize(df_clean, preset='basic')  # Normaliza valores

print(df_clean)
#   nombre         email           telefono     status  \
# 0 juan pérez     juan@email.com  123-456-7890 activo  
# 1 maria garcía   maria@email.com -            activo  
# 2 -              -               -            activo
```

### Ejemplo 2: Preparación para Análisis

```python
from pandas_toolkit.io.readers import CSVReader
from pandas_toolkit.io.base import NormalizationConfig

reader = CSVReader()

# Leer y normalizar en un paso
df = reader.read("ventas.csv", normalize_columns=True)

# Usar preset analysis_ready (reemplaza columnas originales)
df = reader.normalize(df, preset='analysis_ready')

# Ahora df tiene:
# - Columnas normalizadas (sin espacios, lowercase, sin acentos)
# - Valores normalizados (trim, lowercase, nulls estandarizados)
# - Sin columnas duplicadas (_norm)
# - Listo para análisis
```

### Ejemplo 3: Normalización Personalizada

```python
from pandas_toolkit.io.base import NormalizationConfig

# Configuración personalizada
config = NormalizationConfig(
    strings={
        'trim': True,
        'case': 'upper',  # MAYÚSCULAS en lugar de minúsculas
        'remove_special': False
    },
    nulls={
        'standardize': True,
        'values': ['MISSING', 'UNKNOWN', 'N/D', '']  # Valores null específicos
    },
    columns={
        'drop_original': True,  # Reemplazar columnas
        'suffix': '_clean'
    }
)

df = reader.normalize(df, config=config)
```

### Ejemplo 4: Estandarización de Valores Nulos

```python
# Problema: Múltiples representaciones de valores faltantes
data = {
    "Cliente": ["Juan", "N/A", "Maria", "null", "Pedro", "-"],
    "Monto": ["1000", "", "2000", "N/A", "3000", "0"]
}
df = pd.DataFrame(data)

# Solución: Estandarizar nulls
df_clean = reader.normalize(
    df,
    standardize_nulls=True,
    null_values=['MISSING', 'N/D'],  # Valores adicionales
    drop_original=True
)

# Ahora todos los nulls son np.nan
print(df_clean['Cliente'].isna().sum())  # → 3 valores null
```

### Ejemplo 5: Mantener Columnas Originales vs Reemplazarlas

```python
# OPCIÓN A: Mantener originales (default)
df_with_both = reader.normalize(df, drop_original=False)
# Resultado: ['Nombre', 'Email', 'Nombre_norm', 'Email_norm']

# OPCIÓN B: Reemplazar originales
df_replaced = reader.normalize(df, drop_original=True)
# Resultado: ['Nombre', 'Email'] (pero con valores normalizados)

# OPCIÓN C: Usar sufijo personalizado
df_custom = reader.normalize(df, suffix='_clean', drop_original=False)
# Resultado: ['Nombre', 'Email', 'Nombre_clean', 'Email_clean']
```

### Ejemplo 6: Uso Directo de Normalizers (Avanzado)

```python
from pandas_toolkit.io.base.normalizers import (
    ColumnNormalizer,
    StringNormalizer,
    NullNormalizer
)

# Normalizar solo columnas
df = ColumnNormalizer.normalize(df, convert_case="upper")

# Normalizar solo una columna específica
df['nombre'] = StringNormalizer.normalize(
    df['nombre'],
    trim=True,
    convert_case="title"  # Primera letra mayúscula
)

# Estandarizar nulls
df = NullNormalizer.normalize(df, null_values=['MISSING'])

# Obtener resumen de nulls
summary = NullNormalizer.get_null_summary(df)
print(summary)
#   column  null_count  null_percentage
# 0 nombre           2        20.0
# 1 email            1        10.0
```

### Ejemplo 7: Pipeline Completo de Limpieza

```python
from pandas_toolkit.io.readers import CSVReader
from pandas_toolkit.io.base import NormalizationConfig

# 1. Leer datos
reader = CSVReader()
df = reader.read("datos_raw.csv")

# 2. Normalizar columnas
df = reader.normalize_columns(df, convert_case="lower")

# 3. Configurar normalización personalizada
config = NormalizationConfig.from_preset('full')
config.columns['drop_original'] = True  # Modificar preset

# 4. Aplicar normalización
df = reader.normalize(df, config=config)

# 5. Drop empty rows/columns
df = reader.normalize(
    df,
    drop_empty_cols=True,
    drop_empty_rows=True,
    drop_original=True
)

# 6. Exportar limpio
reader.export([df], "datos_clean.xlsx")
```

## 🎨 Comparación de Enfoques

### Enfoque 1: Tradicional (Backward Compatible)
```python
df = reader.read("data.csv", normalize=True, normalize_columns=True)
# ✅ Funciona como siempre
# ⚠️ Menos control sobre opciones
```

### Enfoque 2: Con Preset (Recomendado)
```python
df = reader.read("data.csv", normalize_columns=True)
df = reader.normalize(df, preset='basic')
# ✅ Fácil de usar
# ✅ Configuración consistente
# ✅ Casos de uso predefinidos
```

### Enfoque 3: Con Config (Máximo Control)
```python
config = NormalizationConfig(...)
df = reader.normalize(df, config=config)
# ✅ Control total
# ✅ Reutilizable
# ⚠️ Más verboso
```

### Enfoque 4: Directo (Avanzado)
```python
from pandas_toolkit.io.base.normalizers import ColumnNormalizer
df = ColumnNormalizer.normalize(df)
# ✅ Granular
# ✅ Rápido para casos específicos
# ⚠️ Requiere más conocimiento
```

## 🔍 Casos de Uso Comunes

### Caso 1: EDA Rápido
```python
# Quieres explorar datos rápidamente
df = reader.normalize(df, preset='basic')
```

### Caso 2: Preparar para Machine Learning
```python
# Necesitas datos limpios para modelar
df = reader.normalize(df, preset='analysis_ready')
```

### Caso 3: Mantener Trazabilidad
```python
# Quieres comparar antes/después
df = reader.normalize(df, drop_original=False, suffix='_clean')
# Ahora tienes: valor_original vs valor_original_clean
```

### Caso 4: Limpieza Mínima
```python
# Solo quieres quitar espacios
df = reader.normalize(df, preset='minimal')
```

## 💡 Tips

1. **Usa presets primero**: Prueba `'basic'` o `'full'` antes de customizar
2. **drop_original=True para análisis**: Ahorra memoria y simplifica
3. **Mantén originales para auditoría**: Usa `drop_original=False` (default)
4. **Personaliza presets**: Carga preset y modifica lo que necesites
5. **Revisa nulls primero**: Usa `NullNormalizer.get_null_summary(df)`

## 🐛 Troubleshooting

### Problema: "Los valores no se normalizan"
```python
# Asegúrate de que la columna es tipo string
df['columna'] = df['columna'].astype(str)
df = reader.normalize(df)
```

### Problema: "Perdí mis valores originales"
```python
# Usa drop_original=False (default)
df = reader.normalize(df, drop_original=False)
```

### Problema: "Necesito más control"
```python
# Usa configuración personalizada
config = NormalizationConfig(...)
df = reader.normalize(df, config=config)
```

## 📖 Recursos Adicionales

- [Guía Completa de Normalización](Normalization_Guide.md)
- [Guía de Migración Fase 1](REFACTORING_PHASE1_GUIDE.md)
- [Documentación de Normalizers](../pandas_toolkit/io/base/normalizers/README.md)
- [Resumen Fase 1](PHASE1_SUMMARY.md)

---

¡Disfruta de la nueva funcionalidad de normalización! 🎉
