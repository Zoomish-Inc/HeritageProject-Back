# TODO

## Heritage API detail endpoint alignment (GET /api/v1/heritage/{slug}/)

- [x] 1) Update `heritage/views.py`: remove UUID-based lookup; lookup only by `slug`.
- [x] 2) Update `heritage/views.py`: return 404 JSON wrapper `{success:false, data:null, message:"not_found"}` when not found / not published.
- [x] 3) Ensure `heritage/urls.py` route matches `{slug}` naming (view arg should be `slug`).
- [x] 4) Verify `HeritageObjectSerializer` includes all required text fields for detail page (purpose/style/architect/descriptions/history/mapUrl/tour flags, etc.). If missing, add fields.
- [ ] 5) Run backend tests (and/or minimal curl checks) to verify 200/404 behavior.



