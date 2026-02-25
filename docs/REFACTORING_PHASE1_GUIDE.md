# Refactoring Fase 1 - Guía de Migración

## 🎉 ¿Qué cambió?

La **Fase 1** del refactoring de normalización ha sido completada exitosamente. Se ha reorganizado el código para hacerlo más modular, mantenible y extensible, sin romper la compatibilidad con código existente.

## 📦 Nueva Estructura

### Antes (v1.x)
```
pandas_toolkit/io/base/
  ├── mixins.py  (241 líneas - todo en un archivo)
  └── ...
```

### Ahora (v2.0)
```
pandas_toolkit/io/base/
  ├── mixins.py  (refactorizado - delega a normalizers)
  ├── normalizers/
  │   ├── __init__.py
  │   ├── config.py              # NormalizationConfig (presets y configuración)
  │   ├── column_normalizer.py   # Normalización de nombres de columnas
  │   ├── string_normalizer.py   # Normalización de valores string
  │   └── null_normalizer.py     # Estandarización de valores nulos
  └── ...
```

## ✅ Cambios Implementados

### 1. **Separación de Responsabilidades**
El código de normalización ahora está organizado en módulos especializados:

- **`ColumnNormalizer`**: Normalización de nombres de columnas
- **`StringNormalizer`**: Normalización de valores string (trim, case, special chars)
- **`NullNormalizer`**: Estandarización de valores nulos

### 2. **Sistema de Configuración con Presets**
Nueva clase `NormalizationConfig` con presets predefinidos:

- **`minimal`**: Solo trim básico
- **`basic`**: Trim + case + nulls estándar
- **`full`**: Normalización completa (incluye futuros normalizers)
- **`analysis_ready`**: Optimizado para análisis (drop_original=True)

### 3. **Nuevas Funcionalidades**

#### a) `drop_original` Parameter
```python
# Antes: Siempre creaba columnas con sufijo _norm
df = reader.normalize(df)
# Columnas: ['Name', 'Name_norm']

# Ahora: Opción para reemplazar columnas originales
df = reader.normalize(df, drop_original=True)
# Columnas: ['Name']  (valores normalizados)
```

#### b) Estandarización Mejorada de Nulls
```python
# Convierte múltiples representaciones de null a np.nan
df = reader.normalize(df, standardize_nulls=True)
# '', 'N/A', 'null', 'None', '-', '--' → np.nan

# Valores null personalizados
df = reader.normalize(df, null_values=['MISSING', 'UNKNOWN'])
```

#### c) Sufijo Personalizable
```python
# Antes: Siempre usaba '_norm'
df = reader.normalize(df)
# Columnas: ['Name', 'Name_norm']

# Ahora: Sufijo personalizable
df = reader.normalize(df, suffix='_clean')
# Columnas: ['Name', 'Name_clean']
```

#### d) Presets para Uso Rápido
```python
# Preset básico
df = reader.normalize(df, preset='basic')

# Preset completo
df = reader.normalize(df, preset='full')

# Preset para análisis (reemplaza columnas)
df = reader.normalize(df, preset='analysis_ready')
```

#### e) Configuración con Objetos o Diccionarios
```python
# Usando config object
config = NormalizationConfig(
    strings={'trim': True, 'case': 'upper'},
    nulls={'standardize': True},
    columns={'drop_original': True, 'suffix': '_norm'}
)
df = reader.normalize(df, config=config)

# Usando config dict
config_dict = {
    'strings': {'trim': True, 'case': 'lower'},
    'columns': {'drop_original': False}
}
df = reader.normalize(df, config=config_dict)
```

#### f) Remover caracteres especiales en valores
```python
# Nuevo parámetro en config
config = NormalizationConfig(
    strings={'remove_special': True}
)
df = reader.normalize(df, config=config)
# "user@email.com" → "useremailcom"
```

## 🔄 Compatibilidad Hacia Atrás

### ✅ TODO el código existente sigue funcionando

```python
# Esto sigue funcionando exactamente igual
df = reader.normalize_columns(df)
df = reader.normalize(df, trim_strings=True, convert_case="lower")

# Métodos legacy también funcionan
reader._remove_accents("Café")  # → "Cafe"
reader._handle_duplicate_columns(["name", "name"])  # → ['name', 'name_1']
```

### 📝 No se requieren cambios en código existente

Tu código actual seguirá funcionando sin modificaciones. Las nuevas funcionalidades son **opt-in**.

## 🚀 Guía de Adopción

### Migración Gradual Recomendada

#### Paso 1: Familiarízate con los presets
```python
# Prueba diferentes presets en tu código
df = reader.normalize(df, preset='basic')
df = reader.normalize(df, preset='full')
```

#### Paso 2: Explora drop_original
```python
# Si no necesitas las columnas originales
df = reader.normalize(df, drop_original=True)
```

#### Paso 3: Usa configuración personalizada
```python
# Para casos específicos
config = NormalizationConfig.from_preset('basic')
config.strings['case'] = 'upper'
df = reader.normalize(df, config=config)
```

## 📊 Ejemplos de Uso

### Caso 1: Limpieza Básica (Backward Compatible)
```python
from pandas_toolkit.io.readers import CSVReader

reader = CSVReader()
df = reader.read("data.csv", normalize=True, normalize_columns=True)
# Funciona exactamente igual que antes
```

### Caso 2: Normalización para Análisis
```python
# Reemplaza columnas originales con versiones normalizadas
df = reader.read(
    "data.csv",
    normalize=True,
    normalize_columns=True
)
df = reader.normalize(df, preset='analysis_ready')
```

### Caso 3: Normalización Personalizada
```python
config = NormalizationConfig(
    strings={'trim': True, 'case': 'lower', 'remove_special': False},
    nulls={'standardize': True, 'values': ['MISSING', 'N/A', '']},
    columns={'drop_original': False, 'suffix': '_clean'}
)

df = reader.normalize(df, config=config)
```

### Caso 4: Estandarizar Valores Nulos
```python
# Valores null personalizados para tu dominio
df = reader.normalize(
    df,
    standardize_nulls=True,
    null_values=['UNKNOWN', 'NOT AVAILABLE', '-'],
    drop_original=True
)
```

## 🧪 Tests

Se agregaron **53 nuevos tests** específicos para el refactoring:

- `test_normalization_config.py`: 10 tests para configuración
- `test_normalizers.py`: 23 tests para normalizers especializados
- `test_normalize_mixin_refactored.py`: 20 tests para backward compatibility

**Total: 104 tests pasando ✅**

## 📚 Documentación

### Nuevos módulos exportados
```python
from pandas_toolkit.io.base import (
    NormalizationConfig,     # ← NUEVO
    ColumnNormalizer,        # ← NUEVO
    StringNormalizer,        # ← NUEVO
    NullNormalizer,          # ← NUEVO
)
```

### Uso directo de normalizers (avanzado)
```python
from pandas_toolkit.io.base.normalizers import ColumnNormalizer, NullNormalizer

# Normalizar solo columnas
df = ColumnNormalizer.normalize(df, convert_case="upper")

# Normalizar solo nulls
df = NullNormalizer.normalize(df, null_values=['MISSING'])

# Obtener resumen de nulls
summary = NullNormalizer.get_null_summary(df)
print(summary)
#   column  null_count  null_percentage
# 0      A           2        33.333333
```

## 🔮 Próximos Pasos (Fases Futuras)

### Fase 2: Normalizaciones Core (En desarrollo)
- Normalización de fechas
- Normalización numérica
- Mejoras en manejo de nulls

### Fase 3: Normalizaciones Avanzadas
- Normalización de booleanos
- Detección automática de tipos
- Estandarización de categorías

### Fase 4: Sistema de Reportes
- Reportes detallados de cambios
- Logging de transformaciones
- Estadísticas de normalización

## ❓ FAQ

**P: ¿Debo cambiar mi código existente?**  
R: No, todo el código existente sigue funcionando. Los cambios son retrocompatibles.

**P: ¿Cuándo debo usar `drop_original=True`?**  
R: Úsalo cuando estés seguro de que no necesitas los valores originales y quieres ahorrar memoria.

**P: ¿Qué preset debo usar?**  
R: 
- `minimal`: Para limpieza ligera
- `basic`: Para la mayoría de casos (recomendado por defecto)
- `full`: Para limpieza exhaustiva
- `analysis_ready`: Para preparar datos para análisis (reemplaza columnas)

**P: ¿Puedo crear mis propios presets?**  
R: Sí, puedes extender `_PRESETS` en `config.py` o usar configuración personalizada.

**P: ¿Los métodos `_remove_accents` y `_handle_duplicate_columns` siguen disponibles?**  
R: Sí, están marcados como deprecated pero siguen funcionando para compatibilidad.

## 🐛 Reporte de Issues

Si encuentras algún problema con el refactoring, por favor reporta:
- Descripción del problema
- Código que falló
- Comportamiento esperado vs actual
- Versión anterior que funcionaba (si aplica)

## 📝 Changelog

### v2.0.0 - Fase 1 Refactoring (2026-02-25)

**Added:**
- Sistema de configuración con `NormalizationConfig`
- Presets: `minimal`, `basic`, `full`, `analysis_ready`
- Parámetro `drop_original` para reemplazar columnas
- Parámetro `standardize_nulls` mejorado
- Parámetro `suffix` personalizable
- Soporte para `config` dict/object
- Normalizadores especializados: `ColumnNormalizer`, `StringNormalizer`, `NullNormalizer`
- 53 nuevos tests

**Changed:**
- Refactorizado `NormalizeMixin` para usar normalizers especializados
- Mejorada modularidad del código

**Maintained:**
- 100% compatibilidad hacia atrás
- Todos los métodos existentes siguen funcionando
- Sin breaking changes

---

**¡Gracias por usar la EDA Toolkit!** 🚀
