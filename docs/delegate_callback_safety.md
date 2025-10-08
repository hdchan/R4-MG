# Delegate Callback Safety Pattern

## Overview
When implementing asynchronous operations with delegate callbacks in Qt/PyQt applications, special care must be taken to handle cases where the delegate object may be deleted before the callback completes.

## Problem Statement
In async operations, there's a risk of accessing deleted objects when callbacks complete after the delegate is destroyed. This is particularly common in UI components that may be closed or removed while operations are pending.

## Examples

### Image Preview Generation
```python
# In DraftListImagePreviewViewController
def _generate_image(self):
    def _finished(pixmap: Optional[QPixmap], image: Optional[Image.Image]):
        try:
            # Protected against delegate deletion
            self._image_view.setPhoto(pixmap, None)
            self._sync_spinner()
        except Exception as error:
            print(error)
```

### Search Results Handling
```python
# In SearchTableViewController
def ds_completed_search_with_result(self, result):
    try:
        # Protected against view controller deletion
        self._table_view.update_with_search_results(result)
    except Exception as error:
        print(error)
```

## Implementation Patterns

### 1. Delegate Pattern (1:1)
- Requires explicit try/except handling
- Used for direct callbacks to specific objects
- Example: Image generation completion handlers

### 2. Observer Pattern (Many:Many)
- Handled automatically by ObservationTower
- Used for broadcast events
- Automatically filters deleted observers

## Best Practices

1. **Always Protect Delegate Callbacks**
   - Wrap callback implementations in try/except
   - Log errors for debugging purposes
   - Allow graceful failure

2. **Use ObservationTower When Possible**
   - Prefer observer pattern for loosely coupled components
   - Automatically handles deleted observers
   - Better for broadcast events

3. **Consider Weak References**
   - Use weak references for long-lived delegate relationships
   - Helps prevent memory leaks
   - Automatic cleanup of deleted objects

## Code Example

```python
class SafeDelegateImplementation:
    def async_operation_callback(self):
        try:
            # Perform callback operations
            self.delegate.handle_result()
        except Exception as error:
            print(f"Delegate likely deleted: {error}")
```

## Related Components
- DraftListImagePreviewViewController
- SearchTableViewController
- ObservationTower
- DraftListTabbedPackPreviewViewController