## About

The package implements a file storage for password leak records provided by [HaveIBeenPwned](https://haveibeenpwned.com/).  

## Usage

Firstly, it's necessary to specify storage settings:
```python
from storage.core.models.settings import (
    NumericType,
    PwnedStorageSettings,
    StorageFileQuantity,
)
from storage.pwned_storage import PwnedStorage

settings = PwnedStorageSettings('/tmp/pwned-storage', StorageFileQuantity.N_256, NumericType.SHORT)
storage = PwnedStorage(settings)
```
In this example, storage resources will be located in ***/tmp/pwned-storage***, password leak data will be stored in 256 files and leak occasions will be stored as 2-byte (short) unsigned number (occasion values more than 65535 will be replaced with 65535).

Then, it's possible to request storage update:
```python
response = storage.request_update()
```

Or to request storage update cancellation:
```python
response = storage.request_update_cancellation()
```

Or to get last update status:
```python
revision = storage.revision
```

Or to get leak records:
```python
records = storage.get_range('FADED')
```

For testing purposes mocked version of Pwned requester may be used. Using this version the storage updates much faster:
```python
from storage.mocked.mocked_pwned_requester import MockedPwnedRequester

mocked_storage = PwnedStorage(settings, MockedPwnedRequester())
```

## Package structure

Sub-packages:  
 - **`core/models`** - contains some models necessary for storage.
 - **`mocked`** - contains mocked implementation of storage that updates fast, though, uninformative datasets are produced.
 - **`auxiliary`** - contains only auxiliary components and is considered not to be used directly at all.

Modules:
 - **`pwned_storage`** - contains the file storage implementation.
