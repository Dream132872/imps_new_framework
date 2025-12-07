### Popup System (jQuery + data-attributes)

Attribute-driven popup windows with data passing, reply routing, nested popups, persistent per-popup storage, centering, and named windows.

### Files
- `popup-manager.js`: Core logic (auto-inits on DOM ready)
- `index.html`: Base page demo
- `popup.html`: Popup page demo

### Features
- Open popups via attributes (`data-popup-open`)
- Pass data via JSON or form serialization
- Persistent per-popup data in `localStorage` (cleared only when that popup closes)
- Nested popups (popups can open popups)
- Replies back to the immediate opener; optional controlled bubbling upstream
- Window centering (`data-popup-center`)
- Named popups (`data-popup-name`)
- Per-popup handler functions (`data-popup-handler`) - each popup can have its own unique reply handler

### How it Works
- Each popup has an id (`popupId`). If `data-popup-name` is provided, that exact value is used; otherwise a random id is generated.
- The opener persists sent data under `localStorage["popup:<popupId>:data"]` and opens `popup.html?popupId=<id>`.
- If `data-popup-handler` is specified, the handler function name is stored under `localStorage["popup:<popupId>:handler"]`.
- In the popup, `PopupManager.getData()` reads that payload.
- When a popup replies with `PopupManager.reply(payload)` or via attributes, the message goes to the immediate opener (using `window.opener.postMessage`). The reply includes the `popupId` for routing.
- The opener looks up the handler function name by `popupId` and calls `window[handlerName](payload)`. If no handler is specified, it falls back to the global `window.PopupManager_onReply` function for backward compatibility.
- Parents can optionally forward upstream by returning `{ bubble: true, payload }` from their handler.
- Data and handler name are removed from `localStorage` only when the popup window actually closes (the opener watches `win.closed`). Reloads do not remove data.
- No `parentId` query param is used or required; parent/child relationships rely on `window.opener`.

### Quick Reference (Attributes)
| Attribute | Where | Type | Default | Description |
| --- | --- | --- | --- | --- |
| `data-popup-open` | opener | string (URL) | — | URL to open in a popup (supports nested) |
| `data-popup-features` | opener | string | `width=1000,height=700,resizable=yes,scrollbars=yes` | Native `window.open` features |
| `data-popup-center` | opener | "true" | true | Center popup using width/height; accepts `"true"|"false"`. Bare attribute implies true |
| `data-popup-data` | opener | JSON string | `{}` | Static JSON payload sent to popup and stored |
| `data-popup-data-from` | opener | CSS selector | — | Serialize a form to payload |
| `data-popup-name` | opener | string | random id | Name/id of popup window; reuses same named window if open |
| `data-popup-handler` | opener | string (function name) | — | JavaScript function name to call when this popup replies (e.g., `"handleMyPopupReply"`) |
| `data-popup-reply` | popup | JSON string | `{}` | Reply payload to opener |
| `data-popup-reply-from` | popup | CSS selector | — | Reply with serialized form fields |

### Attributes (Openers)
- `data-popup-open="popup.html"`: URL to open.
- `data-popup-features="width=600,height=500,resizable=yes,scrollbars=yes"`: Native `window.open` features string. Defaults to `width=1000,height=700,resizable=yes,scrollbars=yes` if not specified.
- `data-popup-center`: Center the popup using `width/height` from features (defaults to 520x520). Accepts `"true"|"false"`; default is `true`. Using the bare attribute also implies `true`.
- `data-popup-data='{"k":"v"}'`: JSON payload to send and persist.
- `data-popup-data-from="#formSelector"`: Serialize a form to the payload.
- Alternatively, you can pass a global variable name or dot-path via `data-popup-data` (resolved in the opener). Example: `data-popup-data="myData"` or `data-popup-data="App.state.user"`.
- `data-popup-name="my_popup"`: Name/id of the popup window (reuses the existing named window if open).
- `data-popup-handler="myHandlerFunction"`: JavaScript function name to call when this popup replies. The function must be defined in the global scope (`window.myHandlerFunction`). This allows multiple popups on the same page to have unique handlers without conflicts. If not specified, falls back to global `window.PopupManager_onReply`.

### Attributes (Replies from a popup)
- `data-popup-reply='{"k":"v"}'`: Send static JSON payload back to the opener.
- `data-popup-reply-from="#formSelector"`: Send serialized form fields as payload.

### JavaScript API (in popups)
- `PopupManager.getData()`: Returns data sent to this popup.
- `PopupManager.reply(payload)`: Sends a reply to the immediate opener.

### Reply Handling

#### Per-Popup Handler Functions (Recommended)
Each popup opener can specify its own handler function using `data-popup-handler`:
```html
<button
  data-popup-open="popup.html"
  data-popup-handler="handleMyPopupReply"
  data-popup-name="my_popup">
  Open Popup
</button>
```

```javascript
// Define the handler function in global scope
function handleMyPopupReply(payload) {
  console.log('Reply received:', payload);
  // Handle the reply
  // Return nothing or { bubble: false } to stop.
  // Return { bubble: true, payload } to forward upstream to your opener.
}
```

**Benefits:**
- Each popup can have its own unique handler function
- Multiple popups on the same page won't conflict
- Handler is automatically called when the popup replies

#### Global Handler (Backward Compatibility)
If `data-popup-handler` is not specified, PopupManager falls back to the global handler:
```javascript
window.PopupManager_onReply = function(payload) {
  // Handle the reply locally.
  // Return nothing or { bubble: false } to stop.
  // Return { bubble: true, payload } to forward upstream to your opener.
};
```

**Note:** If multiple popups on the same page use the global handler, they will all share the same function (last one wins), which may cause conflicts. Use `data-popup-handler` to avoid this.

### Examples
Open popup with JSON, centered, named:
```html
<button
  data-popup-open="popup.html"
  data-popup-name="user_profile_popup"
  data-popup-features="width=600,height=500"
  data-popup-center="true"
  data-popup-data='{"userId":123,"from":"base"}'>
  Open User Profile
</button>
```

Open popup using a form as payload:
```html
<form id="userForm">
  <input name="userId" value="123" />
  <input name="note" value="Hello" />
  <!-- include other fields as needed -->
  <button
    type="button"
    data-popup-open="popup.html"
    data-popup-features="width=520,height=520"
    data-popup-center="true"
    data-popup-data-from="#userForm">Open</button>
</form>
```

Reply from popup via attributes:
```html
<button class="btn" data-popup-reply='{"status":"ok"}'>Send Quick Reply</button>
<button class="btn" data-popup-reply-from="#replyForm">Send Form Reply</button>
```

Reply from popup via JS:
```javascript
PopupManager.reply({ status: 'ok', at: Date.now() });
```

Open popup with custom handler function (recommended for multiple popups):
```html
<button
  data-popup-open="popup.html"
  data-popup-name="user_profile_popup"
  data-popup-handler="handleUserProfileReply"
  data-popup-features="width=600,height=500"
  data-popup-data='{"userId":123,"from":"base"}'>
  Open User Profile
</button>
```

```javascript
function handleUserProfileReply(payload) {
  console.log('User profile reply received:', payload);
  // Handle the reply - no return means no bubbling
}
```

Consume replies on the opener using global handler (backward compatibility):
```javascript
window.PopupManager_onReply = function(payload) {
  console.log('Reply received:', payload);
  // stop here (return nothing)
};
```

Forward replies upstream (controlled bubbling):
```javascript
function handleMyPopupReply(payload) {
  // Optionally transform
  const transformed = { fromChild: true, child: payload };
  return { bubble: true, payload: transformed };
}
```

Nested popup reply (non-bubbling in intermediate popup):
```html
<!-- In popup.html (the intermediate parent) -->
<script>
  window.PopupManager_onReply = function(childPayload) {
    console.log('Child replied to me only:', childPayload);
    // Returning nothing prevents bubbling to the base window
  };
</script>
```

Multiple popups on the same page (each with its own handler):
```html
<!-- Form with both Picture and Attachment widgets -->
<form>
  <!-- Picture widget popup -->
  <button
    data-popup-open="/media/picture/create/"
    data-popup-name="select_picture_popup"
    data-popup-handler="handlePicturePopupReply"
    data-popup-data='{"picture_box_id":"pic-123","many":true}'>
    Select Picture
  </button>

  <!-- Attachment widget popup -->
  <button
    data-popup-open="/media/attachment/create/"
    data-popup-name="select_attachment_popup"
    data-popup-handler="handleAttachmentPopupReply"
    data-popup-data='{"attachment_box_id":"att-456","many":true}'>
    Select Attachment
  </button>
</form>
```

```javascript
// Each popup has its own handler - no conflicts!
function handlePicturePopupReply(payload) {
  console.log('Picture selected:', payload);
  // Update picture widget
}

function handleAttachmentPopupReply(payload) {
  console.log('Attachment selected:', payload);
  // Update attachment widget
}
```

### Notes and Tips
- **Per-Popup Handlers**: Use `data-popup-handler` to assign unique handler functions to each popup. This prevents conflicts when multiple popups exist on the same page (e.g., SelectPicture and SelectAttachment widgets).
- **Named windows** (`data-popup-name`) let you reuse existing popups instead of opening duplicates.
- **Handler function scope**: Handler functions specified in `data-popup-handler` must be defined in the global scope (accessible via `window[functionName]`).
- **Fallback behavior**: If no `data-popup-handler` is specified, PopupManager falls back to the global `window.PopupManager_onReply` function for backward compatibility.
- **PopupId routing**: Each reply message includes the `popupId`, allowing PopupManager to route replies to the correct handler function.
- Ensure popups are not blocked: interactions (click) should trigger opening.
- Width/height must be present to center precisely; defaults to 520x520 if omitted.
- Same-origin: For replies and `localStorage` to work seamlessly, popups should be opened from the same origin. Cross-origin windows will not allow direct `localStorage` sharing and may restrict `postMessage` unless you provide an explicit target origin and handle messages accordingly.


