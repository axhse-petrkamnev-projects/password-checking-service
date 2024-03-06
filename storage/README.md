## About

The package implements a file storage for password leak records provided by [HaveIBeenPwned](https://haveibeenpwned.com/).  

## Usage

Firstly, it's necessary to specify storage.
Then, it's possible to get leak record range:
```python
from storage.pwned_storage import PwnedStorage

storage = PwnedStorage('/tmp/pwned-storage')
records = storage.get_range('90ABC')
```

In this example, storage resources will be located in ***/tmp/pwned-storage***.


## Package structure

Sub-packages:  
 - **`core/models`** - contains some models necessary for storage.
 - **`mocked`** - contains mocked implementation of storage that updates fast, though, uninformative datasets are produced.
 - **`auxiliary`** - contains only auxiliary components and is considered not to be used directly at all.

Modules:
 - **`pwned_storage`** - contains the file storage implementation.
