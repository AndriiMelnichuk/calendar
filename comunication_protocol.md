# Comunication protocol
## Task search
``` shelloo
curl -X POST http://localhost:5010/ -H "Content-Type: application/json" -d '{
    "type": "get_all_assigned_task_with_date",
    "jwt": "key"
}'

return_type {
    "id": ["id0", ...],
    "title": ["name0", ...],
    "description": ["desc0", ...],
    "deadline": ["deadline0", ...],
    "assigned": [["member00", "member01", ...], ["member10", ...], ...],
    "status": ["todo_task0", ...]
}
```
## Add event to calendar
``` shelloo
curl -X POST http://localhost:5010/ -H "Content-Type: application/json" -d '{
    "type": "add_event_to_calendar",
    "jwt": "key",
    "access_token": "token",
    "id": ["id0", ...],
    "title": ["name0", ...],
    "description": ["desc0", ...],
    "deadline": ["deadline0", ...],
    "assigned": [["member00", "member01", ...], ["member10", ...], ...],
    "status": ["todo_task0", ...]
}'

return_type {

}

```