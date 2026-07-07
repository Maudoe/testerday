# Guiones de narracion — Laboratorio de seguridad (x1–x50)

Voz ES: `es-US-AlonsoNeural` · Voz EN: `en-US-AndrewNeural` · rate `+0%` · musica: True

> Texto que lee cada audio. En el MP3 las siglas se pronuncian aclaradas (HMAC→hache-mac, etc.).


## x1 — QR de entrega falsificado

**ES:** Alguien podría dibujar o inventar un QR para decir "ya entregué" sin haber entregado nada. El QR tiene que ser imposible de falsificar: lo firma el sistema con una firma que solo él sabe hacer. El caso: Un tercero genera o copia un QR y marca un envío como entregado sin entrega real. La solución: El QR no lleva un simple id: lleva un token firmado por el servidor (HMAC / JWT firmado) que ata shipment_id + tenant + vencimiento. Al escanear, la verificación es siempre del lado del servidor; si el contenido fue alterado, la firma no valida y se rechaza. Un QR dibujado o adivinado nunca produce una firma válida. Y cómo lo prueba el tester: Alterar 1 byte del payload → firma inválida (rechazo). QR sin firma o firmado con otra clave → 401. Nunca validar el QR solo en el teléfono.

**EN (Forged delivery QR):** Someone could draw or invent a QR to say "already delivered" without delivering anything. The QR must be impossible to forge: the system signs it with a signature only it can produce. The case: A third party generates or copies a QR and marks a shipment delivered with no real delivery. The solution: The QR doesn't carry a plain id: it carries a server-signed token (HMAC / signed JWT) binding shipment_id + tenant + expiry. On scan, verification is always server-side; if the content was altered the signature fails and it's rejected. A drawn or guessed QR never produces a valid signature. And how the tester checks it: Flip 1 byte of the payload → invalid signature (reject). QR with no signature or another key → 401. Never validate the QR on the phone alone.


## x2 — Reuso de un QR viejo (replay)

**ES:** Aunque el QR sea legítimo, alguien podría sacarle una foto y reusarlo después. Por eso cada QR sirve una sola vez y por poco tiempo. El caso: Se reutiliza un QR válido (screenshot) para confirmar una entrega vieja o dos veces la misma. La solución: Cada QR es de un solo uso: lleva un nonce y un vencimiento corto, y el servidor lo "quema" en el primer escaneo válido. Un segundo escaneo del mismo token es un no-op rechazado. Así una captura de pantalla reusada no confirma nada, y un token viejo tampoco. Y cómo lo prueba el tester: Escanear el mismo token 2× → el 2do rechazado. Token vencido → rechazo. Ventana de validez acotada y medida.

**EN (Reusing an old QR (replay)):** Even if the QR is legit, someone could screenshot it and reuse it later. That's why each QR works only once and for a short time. The case: A valid QR (screenshot) is reused to confirm an old delivery or the same one twice. The solution: Each QR is single-use: it carries a nonce and a short expiry, and the server burns it on the first valid scan. A second scan of the same token is a rejected no-op. So a reused screenshot confirms nothing, and neither does an old token. And how the tester checks it: Scan the same token 2× → the 2nd rejected. Expired token → reject. Bounded, measured validity window.


## x3 — Deepfake / foto en el escaneo facial

**ES:** Si usamos la cara para confirmar quién entrega, hay que asegurar que es una persona real y viva, no una foto, un video grabado ni un deepfake en una pantalla. El caso: Presentan una foto, un video pregrabado o un deepfake ante la cámara para hacerse pasar por el chofer. La solución: La verificación facial (tipo FaceTec) exige liveness: prueba de que hay una cara 3D real y presente (profundidad, micro-movimiento, challenge-response), no una imagen plana. El match contra la identidad registrada del chofer se hace en el servidor, nunca confiando en un "ok" que manda el teléfono. Foto impresa, replay de video y máscara deben dar rechazo. Y cómo lo prueba el tester: Foto/print → rechazo. Video replay en pantalla → rechazo. Cara real del chofer asignado → match; cara de otro → no-match. El veredicto se decide server-side.

**EN (Deepfake / photo at the face scan):** If we use the face to confirm who delivers, we must ensure it's a real, live person, not a photo, a recorded video or a deepfake on a screen. The case: A photo, a pre-recorded video or a deepfake is shown to the camera to impersonate the driver. The solution: Face verification (FaceTec-style) requires liveness: proof of a real, present 3D face (depth, micro-movement, challenge-response), not a flat image. The match against the driver's enrolled identity is done on the server, never trusting an "ok" the phone sends. A printed photo, a video replay and a mask must all be rejected. And how the tester checks it: Photo/print → reject. On-screen video replay → reject. Assigned driver's real face → match; someone else → no-match. The verdict is decided server-side.


## x4 — El que entrega no es el chofer asignado

**ES:** El que aparece a entregar tiene que ser justo el chofer que el sistema asignó, no cualquiera que tenga el teléfono en la mano. El caso: Otra persona usa la app o el dispositivo del chofer para entregar en su nombre. La solución: La entrega ata tres cosas: el chofer asignado al envío, el dispositivo registrado (device binding) y el match facial en vivo. Si el rostro no coincide con el chofer del envío, la confirmación no se habilita. Se registra quién confirmó, con qué device y con qué resultado biométrico. Y cómo lo prueba el tester: Chofer B intenta cerrar un envío asignado a A → bloqueado. Device no registrado → paso extra o rechazo. La entrega queda atada a la identidad, no al aparato.

**EN (The one delivering isn't the assigned driver):** Whoever shows up to deliver must be exactly the driver the system assigned, not just anyone holding the phone. The case: Another person uses the driver's app or device to deliver in their name. The solution: Delivery binds three things: the assigned driver of the shipment, the registered device (device binding) and the live face match. If the face doesn't match the shipment's driver, confirmation isn't enabled. It records who confirmed, on which device and with what biometric result. And how the tester checks it: Driver B tries to close a shipment assigned to A → blocked. Unregistered device → step-up or reject. Delivery is tied to the identity, not the gadget.


## x5 — Intercepción de datos (man-in-the-middle)

**ES:** Cuando el teléfono le habla al servidor, alguien en la misma red (un wifi público) podría escuchar o cambiar los datos en el camino. Hay que cifrar y verificar bien con quién hablás. El caso: En una red hostil interceptan o alteran el tráfico entre la app y el backend. La solución: Todo va por TLS moderno; la app móvil hace certificate pinning para no aceptar el certificado impostor de un proxy, y el backend fuerza HSTS. No se confía en la red del cliente. Los datos sensibles nunca viajan en la URL ni en claro. Con pinning, un proxy con su propio certificado hace fallar la conexión en vez de exponer los datos. Y cómo lo prueba el tester: Proxy con cert propio (MITM) → la app corta por pinning. Endpoint por http → redirige/rechaza. Ningún dato sensible en la query string ni en logs.

**EN (Data interception (man-in-the-middle)):** When the phone talks to the server, someone on the same network (a public wifi) could listen in or change the data on the way. You must encrypt and verify who you're talking to. The case: On a hostile network, traffic between the app and the backend is intercepted or altered. The solution: Everything goes over modern TLS; the mobile app does certificate pinning so it won't accept a proxy's impostor certificate, and the backend enforces HSTS. The client's network is not trusted. Sensitive data never travels in the URL or in the clear. With pinning, a proxy using its own certificate makes the connection fail instead of exposing the data. And how the tester checks it: Proxy with its own cert (MITM) → the app cuts off via pinning. http endpoint → redirect/reject. No sensitive data in the query string or logs.


## x6 — Robar datos de otro cliente vía token

**ES:** Cada empresa solo puede ver lo suyo. Alguien podría intentar cambiar su credencial para hacerse pasar por otra empresa. Eso tiene que ser imposible. El caso: Manipular el token/JWT (cambiar tenant_id, rol o scope) para leer datos de otro tenant. La solución: El tenant y el rol viven en un token firmado por el servidor; el backend valida la firma y rechaza el algoritmo "none". El tenant se toma del token, nunca de un parámetro que manda el cliente, y toda query filtra por él (defensa en profundidad con row-level security). Un recurso de otro tenant responde 404, no 403. Cambiar un claim rompe la firma → 401. Y cómo lo prueba el tester: Editar tenant_id en el token → 401. Recurso de A con token de B → 404. alg=none → rechazo. Ningún SELECT sin filtro de tenant.

**EN (Stealing another client's data via token):** Each company may only see their own things. Someone could try to change their credential to impersonate another company. That must be impossible. The case: Tamper with the token/JWT (change tenant_id, role or scope) to read another tenant's data. The solution: The tenant and role live in a server-signed token; the backend validates the signature and rejects the "none" algorithm. The tenant is taken from the token, never from a client-supplied parameter, and every query filters by it (defense in depth with row-level security). Another tenant's resource returns 404, not 403. Changing a claim breaks the signature → 401. And how the tester checks it: Edit tenant_id in the token → 401. A's resource with B's token → 404. alg=none → reject. No SELECT without a tenant filter.


## x7 — Falsear la ubicación (GPS / VPN)

**ES:** Alguien podría decir "entregué acá" desde otro lado, falseando el GPS o usando una VPN para simular estar en otro país. Hay que chequear que la ubicación sea creíble. El caso: Se marca la entrega desde una ubicación falsa (mock GPS, VPN, emulador). La solución: La entrega valida un geofence del lado del servidor: la posición reportada tiene que caer cerca del destino esperado, y se cruza con señales independientes (IP vs GPS, timestamps, detección de mock-location / emulador). No se confía solo en las coordenadas que manda el device. Una entrega fuera del geofence queda pendiente de revisión, no confirmada. Y cómo lo prueba el tester: Coordenadas fuera del geofence → no confirma. GPS mockeado / emulador → flag. IP en país A vs GPS en país B → alerta. El geofence se evalúa en el servidor.

**EN (Spoofing the location (GPS / VPN)):** Someone could claim "delivered here" from elsewhere, faking GPS or using a VPN to appear in another country. You must check the location is believable. The case: Delivery is marked from a fake location (mock GPS, VPN, emulator). The solution: Delivery validates a server-side geofence: the reported position must fall near the expected destination, and it's cross-checked against independent signals (IP vs GPS, timestamps, mock-location / emulator detection). The device's coordinates alone aren't trusted. A delivery outside the geofence stays pending review, not confirmed. And how the tester checks it: Coords outside the geofence → no confirm. Mocked GPS / emulator → flag. IP in country A vs GPS in country B → alert. The geofence is evaluated on the server.


## x8 — Ver el POD o la factura de otro (IDOR)

**ES:** Los papeles de una entrega (fotos, firma, factura) no pueden quedar accesibles con solo adivinar un número en la dirección web. El caso: Adivinar la URL/id de un documento y descargar el POD o la factura de otro cliente. La solución: Los documentos no se sirven por id secuencial adivinable: se usan URLs firmadas con vencimiento (signed URL) y cada descarga revalida la pertenencia al tenant. Un id de otro cliente responde 404. Los identificadores son no enumerables (UUID / opacos), así recorrer números no revela nada. Y cómo lo prueba el tester: URL de doc de otro tenant → 404. Signed URL vencida → 403. Enumerar ids → nada. La autorización se revisa en cada descarga, no solo al listar.

**EN (Reading someone else's POD or invoice (IDOR)):** A delivery's paperwork (photos, signature, invoice) cannot be reachable by just guessing a number in the web address. The case: Guess a document's URL/id and download another client's POD or invoice. The solution: Documents aren't served by a guessable sequential id: signed URLs with expiry are used and each download re-validates tenant ownership. Another client's id returns 404. Identifiers are non-enumerable (UUID / opaque), so walking numbers reveals nothing. And how the tester checks it: Another tenant's doc URL → 404. Expired signed URL → 403. Enumerate ids → nothing. Authorization is checked on every download, not just on listing.


## x9 — Fuerza bruta y enumeración

**ES:** Si alguien prueba miles de combinaciones (de un código, un QR o un número de pedido), el sistema tiene que frenarlo antes de que acierte una. El caso: Barrido de OTP / QR / ids para adivinar uno válido o mapear qué existe. La solución: Rate limiting por identidad e IP con 429, lockout progresivo y tokens de alta entropía (no adivinables). Las respuestas no distinguen "no existe" de "no autorizado", para no dar pistas de enumeración. Se alertan los patrones de barrido y los picos anómalos. Y cómo lo prueba el tester: N intentos fallidos → 429 / lockout. Enumerar ids → misma respuesta genérica. Token corto o predecible → rechazado desde el diseño.

**EN (Brute force and enumeration):** If someone tries thousands of combinations (of a code, a QR or an order number), the system must stop them before one hits. The case: Sweeping OTP / QR / ids to guess a valid one or map what exists. The solution: Rate limiting per identity and IP with 429, progressive lockout and high-entropy tokens (unguessable). Responses don't distinguish "doesn't exist" from "not authorized", so they give no enumeration hints. Sweep patterns and anomalous spikes are alerted. And how the tester checks it: N failed attempts → 429 / lockout. Enumerate ids → same generic response. Short or predictable token → rejected by design.


## x10 — Rastro inmutable de la entrega (no repudio)

**ES:** Ante una disputa ("yo nunca recibí eso") hace falta una prueba que nadie haya podido editar después: quién, cuándo, dónde y con qué cara se confirmó la entrega. El caso: Alguien niega o altera una entrega; falta evidencia confiable para resolverla. La solución: Cada confirmación (escaneo, match facial, geolocalización, device) se escribe en un log append-only encadenado por hash: no se puede editar ni borrar sin romper la cadena. Sirve como no repudio y para forensics. La evidencia biométrica se guarda como resultado (match / no-match), no como datos crudos de más de los necesarios. Y cómo lo prueba el tester: Intentar editar/borrar un evento → detectable por hash roto. Reconstruir una entrega end-to-end desde el log. Se guarda lo mínimo necesario (privacy by design).

**EN (Immutable delivery trail (non-repudiation)):** In a dispute ("I never received that") you need proof nobody could edit afterward: who, when, where and with what face the delivery was confirmed. The case: Someone denies or alters a delivery; there's no reliable evidence to settle it. The solution: Each confirmation (scan, face match, geolocation, device) is written to an append-only, hash-chained log: it can't be edited or deleted without breaking the chain. It serves as non-repudiation and for forensics. Biometric evidence is stored as a result (match / no-match), not as more raw data than needed. And how the tester checks it: Try to edit/delete an event → detectable via broken hash. Reconstruct a delivery end-to-end from the log. Store the minimum needed (privacy by design).


## x11 — Credential stuffing (contraseñas robadas)

**ES:** La gente repite la misma contraseña en muchos sitios. Si a otro sitio le robaron esa clave, alguien la prueba acá. Hay que frenar el aluvión y sumar un segundo factor. El caso: Prueban miles de usuario+contraseña filtrados de otras brechas para entrar. La solución: MFA en cuentas sensibles, chequeo contra listas de contraseñas comprometidas, rate limit y lockout por IP e identidad, y detección de login anómalo (device/geo nuevos → step-up). Nunca revelar si el usuario existe. La clave sola no alcanza para entrar. Y cómo lo prueba el tester: Aluvión de logins → 429/lockout. Login desde device/país nuevo → pide 2do factor. Usuario inexistente y contraseña mala → misma respuesta.

**EN (Credential stuffing (stolen passwords)):** People reuse the same password across sites. If another site got breached, someone tries it here. You must throttle the flood and add a second factor. The case: Thousands of leaked user+password pairs from other breaches are tried to get in. The solution: MFA on sensitive accounts, checks against breached-password lists, rate limit and lockout per IP and identity, and anomalous-login detection (new device/geo → step-up). Never reveal whether the user exists. The password alone isn't enough. And how the tester checks it: Login flood → 429/lockout. Login from new device/country → asks for 2nd factor. Nonexistent user and wrong password → same response.


## x12 — Robo de sesión (token robado)

**ES:** Si alguien te roba el "pase" de sesión, entra como vos. El pase tiene que durar poco, atarse a tu dispositivo y poder anularse al instante. El caso: Un token/cookie de sesión filtrado se reusa desde otra máquina. La solución: Tokens de vida corta con refresh rotativo (rotation + reuse-detection: si reaparece un refresh viejo, se mata toda la familia). Cookies HttpOnly + Secure + SameSite, sesión atada a device/UA y una lista de revocación para cerrar sesiones ya. Logout invalida en el servidor, no solo en el cliente. Y cómo lo prueba el tester: Reusar un refresh rotado → toda la sesión revocada. Logout → el token viejo da 401. Cookie sin HttpOnly → flag.

**EN (Session hijacking (stolen token)):** If someone steals your session "pass", they're in as you. The pass must be short-lived, tie to your device and be revocable instantly. The case: A leaked session token/cookie is reused from another machine. The solution: Short-lived tokens with rotating refresh (rotation + reuse-detection: if an old refresh reappears, kill the whole family). Cookies HttpOnly + Secure + SameSite, session bound to device/UA and a revocation list to close sessions now. Logout invalidates server-side, not just client-side. And how the tester checks it: Reuse a rotated refresh → whole session revoked. Logout → old token gives 401. Cookie without HttpOnly → flag.


## x13 — Escalada de privilegios

**ES:** Un usuario común no puede, cambiando algo a mano, hacer cosas de administrador ni tocar lo de otra empresa. Los permisos se deciden en el servidor, no en la pantalla. El caso: Un rol básico llama a un endpoint de admin (vertical) u opera recursos ajenos (horizontal). La solución: RBAC del lado del servidor, deny-by-default: cada endpoint declara el permiso que exige y se valida contra el rol del token. El menú oculto en la UI no es un control de seguridad. Se revisa por matriz rol×endpoint que ningún rol acceda de más. Y cómo lo prueba el tester: Rol viewer → POST admin → 403. Matriz rol×endpoint sin huecos. Ocultar el botón no habilita saltarse el check.

**EN (Privilege escalation):** A normal user can't, by tweaking something by hand, do admin things or touch another company's data. Permissions are decided on the server, not in the screen. The case: A basic role calls an admin endpoint (vertical) or operates others' resources (horizontal). The solution: Server-side RBAC, deny-by-default: each endpoint declares the permission it needs and validates it against the token's role. A hidden UI menu is not a security control. A role×endpoint matrix verifies no role over-reaches. And how the tester checks it: Viewer role → admin POST → 403. Role×endpoint matrix with no gaps. Hiding the button doesn't let you skip the check.


## x14 — MFA fatigue (bombardeo de push)

**ES:** Si el 2do factor es apretar "sí" en el celular, un atacante manda push tras push hasta que la víctima, cansada, aprueba una. Hay que cortar eso. El caso: Spam de solicitudes push para que el usuario apruebe una por error. La solución: Number matching (el usuario tipea un número que muestra la pantalla, no solo "aprobar"), límite de intentos por ventana, y alerta al usuario ante muchos pushes. Mejor aún: factores phishing-resistant (passkeys/WebAuthn) que no dependen de aprobar a ciegas. Y cómo lo prueba el tester: N pushes en corto → bloqueo + alerta. Aprobar sin el número correcto → falla. Passkey no aprobable a ciegas.

**EN (MFA fatigue (push bombing)):** If the 2nd factor is tapping "yes" on the phone, an attacker sends push after push until the tired victim approves one. You must stop that. The case: Spamming push requests so the user approves one by mistake. The solution: Number matching (the user types a number shown on screen, not just "approve"), attempt limits per window, and alerting the user on many pushes. Even better: phishing-resistant factors (passkeys/WebAuthn) that don't rely on blind approval. And how the tester checks it: N pushes in a short window → block + alert. Approve without the right number → fails. Passkey isn't blind-approvable.


## x15 — Reset de contraseña inseguro

**ES:** El link para "recuperar contraseña" tiene que ser corto, de un solo uso y difícil de adivinar, y no debe delatar quién tiene cuenta. El caso: Adivinar/reutilizar el token de reset para tomar la cuenta de otro. La solución: Token de reset de alta entropía, un solo uso, vencimiento corto, invalidado al cambiar la clave. La respuesta de "te enviamos un mail" es igual exista o no el usuario (anti-enumeración). Al resetear, se cierran las sesiones activas. Y cómo lo prueba el tester: Token reusado o vencido → rechazo. Email inexistente → misma respuesta genérica. Tras reset → sesiones viejas caídas.

**EN (Insecure password reset):** The "recover password" link must be short, single-use and hard to guess, and must not reveal who has an account. The case: Guess/reuse the reset token to take over someone's account. The solution: High-entropy, single-use reset token, short expiry, invalidated on password change. The "we sent an email" response is the same whether or not the user exists (anti-enumeration). On reset, active sessions are closed. And how the tester checks it: Reused or expired token → reject. Nonexistent email → same generic response. After reset → old sessions dropped.


## x16 — OAuth mal configurado (carrier)

**ES:** Cuando conectás con un tercero (una app de carrier), el "handshake" tiene que verificar bien a dónde vuelve y de quién viene, o alguien roba el permiso. El caso: redirect_uri abierto o falta de state permiten robar el código de autorización. La solución: Validar redirect_uri contra una allowlist exacta, exigir el parámetro state (anti-CSRF) y usar PKCE en clientes públicos/móviles. Scopes mínimos, tokens que vencen y nada de secretos embebidos en la app. El code es de un solo uso. Y cómo lo prueba el tester: redirect_uri no listado → rechazo. Falta state → rechazo. Reusar el code → falla. Scope de más → 403.

**EN (Misconfigured OAuth (carrier)):** When you connect a third party (a carrier app), the "handshake" must properly verify where it returns and who it's from, or someone steals the grant. The case: An open redirect_uri or missing state lets the authorization code be stolen. The solution: Validate redirect_uri against an exact allowlist, require the state parameter (anti-CSRF) and use PKCE on public/mobile clients. Minimal scopes, expiring tokens, and no secrets embedded in the app. The code is single-use. And how the tester checks it: Unlisted redirect_uri → reject. Missing state → reject. Reuse the code → fails. Excess scope → 403.


## x17 — API keys / secretos filtrados

**ES:** Las "llaves" del sistema (claves de API, del banco, de mapas) no pueden estar escritas en el código ni dentro de la app móvil, donde cualquiera las extrae. El caso: Una API key hardcodeada en el repo o en el APK se extrae y se usa. La solución: Secretos en un vault (o variables gestionadas), nunca en el código ni en el cliente; rotación periódica y revocación inmediata al filtrarse. Secret scanning en CI para frenar commits con claves. Las operaciones sensibles se firman en el servidor, no con una key que viaja al teléfono. Y cómo lo prueba el tester: Secret scanner bloquea un commit con key. Key rotada → la vieja deja de funcionar. Grep del APK no revela secretos vivos.

**EN (Leaked API keys / secrets):** The system's "keys" (API, bank, maps) can't be written in the code or inside the mobile app, where anyone extracts them. The case: An API key hardcoded in the repo or the APK is extracted and used. The solution: Secrets in a vault (or managed variables), never in code or the client; periodic rotation and immediate revocation on leak. Secret scanning in CI to block commits with keys. Sensitive ops are signed on the server, not with a key that travels to the phone. And how the tester checks it: Secret scanner blocks a commit with a key. Rotated key → the old one stops working. Grepping the APK reveals no live secrets.


## x18 — SQL injection

**ES:** Si el sistema arma sus consultas pegando texto que escribió el usuario, alguien puede meter comandos y leer o borrar la base. Hay que separar el dato de la orden. El caso: Un campo (referencia, búsqueda) altera la consulta y expone/rompe datos. La solución: Consultas parametrizadas (prepared statements) siempre: el dato del usuario nunca se concatena en el SQL. ORM con binding, validación de entrada y mínimos privilegios del usuario de base. Un ataque clásico (' OR 1=1 --) debe tratarse como texto literal, no como código. Y cómo lo prueba el tester: Payloads de inyección en cada input → se guardan como texto, cero filas de más. Sin string-building de SQL en el código.

**EN (SQL injection):** If the system builds its queries by gluing text the user wrote, someone can inject commands and read or delete the database. You must separate data from command. The case: A field (reference, search) alters the query and exposes/breaks data. The solution: Parameterized queries (prepared statements) always: user data is never concatenated into SQL. ORM with binding, input validation and least privilege for the DB user. A classic attack (' OR 1=1 --) must be treated as literal text, not code. And how the tester checks it: Injection payloads in each input → stored as text, zero extra rows. No SQL string-building in the code.


## x19 — XSS almacenado (notas/direcciones)

**ES:** Si alguien escribe código malicioso en un campo (una nota, una dirección) y otro lo ve en el panel, ese código podría ejecutarse en la sesión del segundo. Hay que "neutralizar" lo que se muestra. El caso: Un script en un campo se ejecuta cuando un operador abre el registro. La solución: Escapar/codificar la salida según el contexto (HTML, atributo, JS), una CSP estricta que bloquee scripts inline, y sanitizado del HTML permitido. Nunca insertar entrada del usuario con innerHTML sin limpiar. El input se guarda; el riesgo está en cómo se renderiza. Y cómo lo prueba el tester: Guardar <script> en un campo → se muestra como texto, no ejecuta. CSP bloquea inline. Auditar cada punto de render.

**EN (Stored XSS (notes/addresses)):** If someone writes malicious code in a field (a note, an address) and another sees it in the panel, that code could run in the second person's session. You must "neutralize" what's displayed. The case: A script in a field runs when an operator opens the record. The solution: Escape/encode output per context (HTML, attribute, JS), a strict CSP that blocks inline scripts, and sanitizing of any allowed HTML. Never insert user input via innerHTML unclean. Input is stored; the risk is in how it's rendered. And how the tester checks it: Store <script> in a field → shown as text, doesn't run. CSP blocks inline. Audit every render point.


## x20 — CSV/Formula injection (exports)

**ES:** Cuando exportás datos a Excel, un campo que empieza con = + - @ puede convertirse en una fórmula peligrosa al abrir el archivo. Hay que desactivarlo. El caso: Un valor guardado se ejecuta como fórmula en la PC de quien abre el CSV. La solución: Al exportar, se neutralizan las celdas que arrancan con caracteres de fórmula (prefijo apóstrofo o escape) y se envuelven en comillas. Es un riesgo de salida, no de la app: se prueba en el archivo generado, no solo en pantalla. Y cómo lo prueba el tester: Campo =cmd() exportado → abre como texto inofensivo, no como fórmula. Revisar el CSV real, no la vista web.

**EN (CSV/Formula injection (exports)):** When you export data to Excel, a field starting with = + - @ can become a dangerous formula when the file opens. You must disable it. The case: A stored value runs as a formula on the machine of whoever opens the CSV. The solution: On export, cells starting with formula characters are neutralized (apostrophe prefix or escaping) and wrapped in quotes. It's an output risk, not an app one: test it in the generated file, not just on screen. And how the tester checks it: Field =cmd() exported → opens as harmless text, not a formula. Check the actual CSV, not the web view.


## x21 — XXE en EDI/XML

**ES:** Los intercambios con socios (EDI) usan archivos XML. Un XML malicioso puede pedirle al sistema que lea archivos internos o golpee la red interna. Hay que apagar esa capacidad. El caso: Un XML entrante con entidades externas lee archivos del servidor o hace SSRF. La solución: Deshabilitar entidades externas y DTD en el parser (XXE off), validar contra schema, límites de tamaño/anidamiento (billion laughs) y correr el parseo con mínimos privilegios. Nunca confiar en el XML de un socio como seguro. Y cómo lo prueba el tester: XML con entidad externa → ignorada/rechazada, cero lectura de archivos. XML gigante/anidado → cortado por límites.

**EN (XXE in EDI/XML):** Partner exchanges (EDI) use XML files. A malicious XML can ask the system to read internal files or hit the internal network. You must turn that capability off. The case: An inbound XML with external entities reads server files or does SSRF. The solution: Disable external entities and DTDs in the parser (XXE off), validate against a schema, size/nesting limits (billion laughs) and parse with least privilege. Never trust a partner's XML as safe. And how the tester checks it: XML with external entity → ignored/rejected, zero file reads. Huge/nested XML → cut by limits.


## x22 — SSRF (URL en webhooks/campos)

**ES:** Si el sistema "va a buscar" una URL que puso el usuario, alguien puede apuntarla a la red interna (o a la metadata del cloud) y hacer que el servidor filtre secretos. El caso: Una URL de webhook/imagen apunta a 169.254.169.254 o a servicios internos. La solución: Allowlist de destinos, resolver el DNS y bloquear rangos internos (loopback, privados, link-local), prohibir redirects a internos y no devolver el cuerpo crudo. La metadata del cloud debe ser inalcanzable desde la app. Y cómo lo prueba el tester: Webhook a IP interna/metadata → bloqueado. Redirect a interno → cortado. URL pública válida → OK.

**EN (SSRF (URL in webhooks/fields)):** If the system "goes and fetches" a user-supplied URL, someone can point it at the internal network (or cloud metadata) and make the server leak secrets. The case: A webhook/image URL points to 169.254.169.254 or internal services. The solution: Destination allowlist, resolve DNS and block internal ranges (loopback, private, link-local), forbid redirects to internal, and don't return the raw body. Cloud metadata must be unreachable from the app. And how the tester checks it: Webhook to internal IP/metadata → blocked. Redirect to internal → cut. Valid public URL → OK.


## x23 — Path traversal (subida/descarga)

**ES:** Un nombre de archivo con ../../ puede hacer que el sistema lea o escriba fuera de la carpeta permitida. Hay que normalizar y encerrar todo en su lugar. El caso: Un nombre malicioso escapa del directorio y accede a archivos del sistema. La solución: Canonicalizar la ruta y verificar que quede dentro del directorio permitido, ignorar el nombre que manda el cliente (usar id propio), y guardar fuera del web-root. Nada de concatenar rutas con input crudo. Y cómo lo prueba el tester: Nombre con ../ → normalizado, no escapa. Descargar fuera del base dir → 404. El nombre del cliente no define la ruta.

**EN (Path traversal (upload/download)):** A filename with ../../ can make the system read or write outside the allowed folder. You must normalize and confine everything. The case: A malicious name escapes the directory and reaches system files. The solution: Canonicalize the path and verify it stays inside the allowed directory, ignore the client-supplied name (use your own id), and store outside the web-root. No concatenating paths with raw input. And how the tester checks it: Name with ../ → normalized, doesn't escape. Download outside the base dir → 404. The client's name doesn't define the path.


## x24 — Deserialización insegura

**ES:** Recibir un objeto "empaquetado" de afuera y reconstruirlo a ciegas puede ejecutar código. Mejor recibir datos simples y validarlos. El caso: Un payload serializado malicioso ejecuta código al deserializarse. La solución: Evitar deserialización nativa de datos no confiables; usar formatos de datos (JSON) con parser seguro, validar contra schema y, si hace falta objetos, allowlist de tipos. Nunca deserializar directo lo que llega por la red. Y cómo lo prueba el tester: Payload con tipo no permitido → rechazado. Fuzzing del endpoint no ejecuta código. Solo tipos esperados se aceptan.

**EN (Insecure deserialization):** Receiving a "packaged" object from outside and rebuilding it blindly can execute code. Better to receive simple data and validate it. The case: A malicious serialized payload runs code when deserialized. The solution: Avoid native deserialization of untrusted data; use data formats (JSON) with a safe parser, validate against a schema and, if objects are needed, allowlist types. Never deserialize network input directly. And how the tester checks it: Payload with a disallowed type → rejected. Fuzzing the endpoint runs no code. Only expected types are accepted.


## x25 — Command injection (labels/PDF)

**ES:** Si para generar una etiqueta o PDF el sistema llama a un programa pegándole texto del usuario, alguien puede colar comandos del sistema operativo. El caso: Un campo se cuela en una llamada de shell al generar un documento. La solución: No invocar el shell con texto interpolado: usar APIs que pasan argumentos como lista (sin shell), validar/allowlist de entradas y correr con mínimos privilegios. Idealmente, librerías nativas en vez de comandos externos. Y cómo lo prueba el tester: Campo con ; rm ... → tratado como dato, no ejecuta. Sin shell=true con input. Generación aislada y con permisos mínimos.

**EN (Command injection (labels/PDF)):** If, to generate a label or PDF, the system calls a program gluing user text into it, someone can slip in OS commands. The case: A field slips into a shell call while generating a document. The solution: Don't invoke the shell with interpolated text: use APIs that pass arguments as a list (no shell), validate/allowlist inputs and run with least privilege. Ideally, native libraries instead of external commands. And how the tester checks it: Field with ; rm ... → treated as data, doesn't run. No shell=true with input. Isolated, least-privilege generation.


## x26 — Subida de archivo malicioso (POD)

**ES:** La foto de una entrega podría ser en realidad un programa disfrazado. Hay que verificar que sea una imagen de verdad y guardarla donde no pueda ejecutarse. El caso: Un webshell subido como "foto de POD" se ejecuta desde el servidor. La solución: Validar tipo real por magic bytes (no por extensión), límite de tamaño, re-encodear la imagen, nombre propio, y guardar en storage fuera del web-root sin permiso de ejecución. Escaneo antivirus y servido con Content-Type correcto. Y cómo lo prueba el tester: .php renombrado a .jpg → rechazado por magic bytes. Archivo subido no es ejecutable ni accesible como URL directa.

**EN (Malicious file upload (POD)):** A delivery photo could actually be a disguised program. You must verify it's a real image and store it where it can't run. The case: A webshell uploaded as a "POD photo" runs from the server. The solution: Validate real type by magic bytes (not extension), size limit, re-encode the image, own filename, and store in off-web-root storage with no execute permission. Antivirus scan and serve with the correct Content-Type. And how the tester checks it: .php renamed to .jpg → rejected by magic bytes. Uploaded file isn't executable nor reachable as a direct URL.


## x27 — PII/secretos en los logs

**ES:** Los registros técnicos (logs) no pueden guardar datos personales, tokens ni contraseñas en claro. Si se filtra un log, no debe entregar información sensible. El caso: Un log guarda el body completo con DNI, teléfonos o tokens. La solución: Redacción automática de campos sensibles, logging estructurado con allowlist de qué se guarda, y nunca loguear cuerpos de auth. Acceso a logs restringido y con retención acotada. Los errores llevan traceId, no datos personales. Y cómo lo prueba el tester: Forzar error/flujo con PII → logs sin PII ni tokens. Grep de logs por patrones sensibles → cero. Acceso auditado.

**EN (PII/secrets in logs):** Technical logs can't store personal data, tokens or passwords in the clear. If a log leaks, it must not hand over sensitive info. The case: A log stores the full body with IDs, phone numbers or tokens. The solution: Automatic redaction of sensitive fields, structured logging with an allowlist of what's stored, and never logging auth bodies. Log access restricted with bounded retention. Errors carry a traceId, not personal data. And how the tester checks it: Force an error/flow with PII → logs without PII or tokens. Grep logs for sensitive patterns → zero. Access audited.


## x28 — Cifrado en reposo

**ES:** Si roban un disco o una copia de la base, los datos tienen que estar cifrados para que no sirvan. Los más sensibles, con protección extra. El caso: Un backup o volumen robado expone datos por estar en claro. La solución: Cifrado en reposo de base, discos y backups, con claves en un KMS y rotación. Campos ultra-sensibles con cifrado a nivel de aplicación/tokenización. Separar claves de datos: quien accede al dato no accede a la clave. Y cómo lo prueba el tester: Volcado crudo del storage → ilegible sin claves. Campo sensible en la tabla → tokenizado/cifrado, no en claro.

**EN (Encryption at rest):** If a disk or a DB copy is stolen, the data must be encrypted so it's useless. The most sensitive, with extra protection. The case: A stolen backup or volume exposes data because it's in the clear. The solution: At-rest encryption of DB, disks and backups, with keys in a KMS and rotation. Ultra-sensitive fields with app-level encryption/tokenization. Separate keys from data: whoever accesses the data doesn't access the key. And how the tester checks it: Raw storage dump → unreadable without keys. Sensitive field in the table → tokenized/encrypted, not in the clear.


## x29 — Backups/exports que filtran datos

**ES:** Las copias de seguridad y los reportes exportados son una base entera afuera. Deben cifrarse, tener dueño y no quedar en un bucket público. El caso: Un bucket de backups o un export mal compartido queda accesible. La solución: Backups cifrados y con acceso restringido, buckets privados por defecto (bloqueo de acceso público), exports con expiración y por tenant, y pruebas de restore. Un export cruza fronteras: aplica minimización y las mismas reglas de tenant. Y cómo lo prueba el tester: Bucket de backups → no público. Export de tenant A no contiene filas de B. Restore probado y auditado.

**EN (Backups/exports leaking data):** Backups and exported reports are a whole database outside. They must be encrypted, owned and never left in a public bucket. The case: A backup bucket or a mis-shared export becomes accessible. The solution: Encrypted, access-restricted backups, private-by-default buckets (public-access block), per-tenant exports with expiry, and tested restores. An export crosses boundaries: apply minimization and the same tenant rules. And how the tester checks it: Backup bucket → not public. Tenant A's export contains no B rows. Restore tested and audited.


## x30 — GDPR / derecho al olvido (PII del chofer)

**ES:** Guardamos datos de personas (choferes, contactos). Hay que guardar solo lo necesario, por el tiempo justo, y poder borrarlos si lo piden. El caso: Un chofer pide borrado y su PII sigue esparcida en tablas y logs. La solución: Minimización y limitación de propósito, política de retención con purga automática, y un flujo de borrado/anonimización que alcanza también backups y logs (o los caduca). Consentimiento y registro de tratamiento. La biometría se guarda como resultado, no cruda. Y cómo lo prueba el tester: Solicitud de borrado → PII eliminada/anonimizada en todas las tablas; queda registro del pedido. Datos vencidos purgados.

**EN (GDPR / right to be forgotten (driver PII)):** We store people's data (drivers, contacts). You must keep only what's needed, for the right time, and be able to delete it on request. The case: A driver requests deletion and their PII lingers across tables and logs. The solution: Minimization and purpose limitation, a retention policy with auto-purge, and a delete/anonymize flow that also reaches backups and logs (or expires them). Consent and processing records. Biometrics stored as a result, not raw. And how the tester checks it: Deletion request → PII removed/anonymized across all tables; the request is logged. Expired data purged.


## x31 — Dependencia vulnerable

**ES:** El sistema usa muchas piezas de terceros (librerías). Si una tiene un agujero conocido, hereda el riesgo. Hay que saber qué usamos y parchear. El caso: Una librería con CVE conocido queda sin actualizar en producción. La solución: SCA en CI que falla ante vulnerabilidades críticas, un SBOM para saber qué se usa, versiones fijadas y actualizaciones regulares. Verificar integridad/firmas de los paquetes. La ventana entre CVE publicado y parche es el riesgo a medir. Y cómo lo prueba el tester: Dependencia con CVE crítico → pipeline falla. SBOM generado por build. Lockfile fija versiones; update rompe el build si algo no cuadra.

**EN (Vulnerable dependency):** The system uses many third-party pieces (libraries). If one has a known hole, you inherit the risk. You must know what you use and patch. The case: A library with a known CVE stays un-updated in production. The solution: SCA in CI that fails on critical vulns, an SBOM to know what's used, pinned versions and regular updates. Verify package integrity/signatures. The window between a published CVE and the patch is the risk to measure. And how the tester checks it: Dependency with a critical CVE → pipeline fails. SBOM generated per build. Lockfile pins versions; an update breaks the build if something's off.


## x32 — Webhook entrante falsificado

**ES:** Cuando un proveedor nos "avisa" algo por webhook, hay que estar seguros de que el aviso vino de él y no de un impostor. El caso: Alguien manda un webhook falso ("entregado", "pagado") haciéndose pasar por el proveedor. La solución: Verificar la firma HMAC del webhook con el secreto compartido, chequear timestamp (anti-replay) y idempotencia por eventId. Allowlist de origen donde aplique. Un webhook sin firma válida se descarta antes de procesar. Y cómo lo prueba el tester: Webhook sin firma o con firma mala → rechazado. Reenvío del mismo eventId → 1 efecto. Timestamp viejo → rechazo.

**EN (Forged inbound webhook):** When a provider "notifies" us via webhook, we must be sure the notice came from them and not an impostor. The case: Someone sends a fake webhook ("delivered", "paid") impersonating the provider. The solution: Verify the webhook's HMAC signature with the shared secret, check the timestamp (anti-replay) and idempotency by eventId. Source allowlist where applicable. A webhook without a valid signature is dropped before processing. And how the tester checks it: Webhook without a signature or a bad one → rejected. Resend of the same eventId → 1 effect. Old timestamp → reject.


## x33 — Suplantación de socio EDI

**ES:** Los mensajes entre empresas (EDI) tienen que probar quién los manda. Si no, un impostor podría inyectar pedidos o cambios de estado. El caso: Un tercero inyecta mensajes EDI haciéndose pasar por un socio real. La solución: mTLS (certificados de ambos lados) o mensajes firmados, validación de schema y de identidad del socio, e idempotencia. Cada socio tiene sus credenciales y su scope; un mensaje sin identidad válida no entra al flujo. Y cómo lo prueba el tester: Mensaje sin cert/firma válida → rechazado. Socio A no puede crear pedidos como socio B. Schema inválido → cae en rechazados.

**EN (EDI partner spoofing):** Messages between companies (EDI) must prove who sends them. Otherwise an impostor could inject orders or status changes. The case: A third party injects EDI messages impersonating a real partner. The solution: mTLS (certs on both sides) or signed messages, schema and partner-identity validation, and idempotency. Each partner has its own credentials and scope; a message without valid identity doesn't enter the flow. And how the tester checks it: Message without a valid cert/signature → rejected. Partner A can't create orders as partner B. Invalid schema → to rejected.


## x34 — JS/CDN de terceros comprometido

**ES:** Si la web carga un script de otra página y esa página es hackeada, el código malo corre en la nuestra. Hay que fijar y verificar lo que cargamos. El caso: Un CDN comprometido sirve un script alterado que roba datos del panel. La solución: Subresource Integrity (SRI) para que el navegador rechace un script alterado, preferir self-hosting de assets críticos, una CSP que limite orígenes, y minimizar terceros. Menos scripts ajenos = menos superficie. Y cómo lo prueba el tester: Script con hash SRI que no coincide → el navegador lo bloquea. CSP rechaza orígenes no listados. Inventario de terceros.

**EN (Compromised third-party JS/CDN):** If the site loads a script from another site and that site is hacked, the bad code runs on ours. You must pin and verify what you load. The case: A compromised CDN serves an altered script that steals dashboard data. The solution: Subresource Integrity (SRI) so the browser rejects an altered script, prefer self-hosting critical assets, a CSP that limits origins, and minimize third parties. Fewer external scripts = less surface. And how the tester checks it: Script whose SRI hash doesn't match → the browser blocks it. CSP rejects unlisted origins. Third-party inventory.


## x35 — Config por defecto / admin expuesto

**ES:** Muchos hackeos entran por una puerta que quedó abierta: un panel de admin, una consola o credenciales por defecto que nadie cerró. El caso: Un actuator/consola o cuenta por defecto queda accesible sin auth. La solución: Hardening: deshabilitar lo que no se usa, cambiar credenciales por defecto, endpoints de gestión (actuator, health interno) autenticados y no expuestos, cabeceras de seguridad y errores sin detalles internos. Baseline de configuración versionado. Y cómo lo prueba el tester: /actuator o consola desde afuera → 401/404. Sin cuentas por defecto vivas. Escaneo de config contra el baseline.

**EN (Default config / exposed admin):** Many hacks come through a door left open: an admin panel, a console or default credentials nobody closed. The case: An actuator/console or default account is reachable without auth. The solution: Hardening: disable what's unused, change default credentials, management endpoints (actuator, internal health) authenticated and not exposed, security headers and errors without internal details. A versioned config baseline. And how the tester checks it: /actuator or console from outside → 401/404. No live default accounts. Config scanned against the baseline.


## x36 — Onboarding de carrier falso (KYC)

**ES:** Antes de darle carga a una empresa de transporte, hay que verificar que sea real y no una fachada para robar el envío. El caso: Un carrier fraudulento se registra con documentos falsos para llevarse la carga. La solución: KYC/KYB: verificación de documentos y de la empresa, validación de identidad del representante, chequeo contra listas y señales de riesgo, y aprobación gradual (límites bajos al inicio). La identidad verificada se ata a las asignaciones posteriores. Y cómo lo prueba el tester: Documento falso/no verificable → onboarding bloqueado o en revisión. Carrier nuevo → límites y monitoreo hasta ganar confianza.

**EN (Fake carrier onboarding (KYC)):** Before giving cargo to a transport company, you must verify it's real and not a front to steal the shipment. The case: A fraudulent carrier registers with fake documents to make off with the cargo. The solution: KYC/KYB: document and business verification, representative identity validation, checks against lists and risk signals, and gradual approval (low limits at first). The verified identity is tied to later assignments. And how the tester checks it: Fake/unverifiable document → onboarding blocked or under review. New carrier → limits and monitoring until trust is earned.


## x37 — Doble brokering / robo de carga

**ES:** Un intermediario acepta un envío y se lo pasa a un tercero desconocido sin permiso, o alguien se hace pasar por el transportista que va a retirar. Así se roba carga. El caso: La carga se entrega a un transportista que no es el verificado/asignado. La solución: Atar el retiro a la identidad verificada del carrier/chofer (el mismo device+face binding de la entrega), PIN de retiro compartido solo con el asignado, y prohibir el re-brokering sin aprobación registrada. Cross-check de la empresa que efectivamente aparece. Y cómo lo prueba el tester: Retiro por transportista no verificado → bloqueado. Sin PIN correcto → no se libera. Re-asignación sin aprobación → rechazada y auditada.

**EN (Double brokering / cargo theft):** A broker accepts a shipment and hands it to an unknown third party without permission, or someone poses as the carrier picking up. That's how cargo gets stolen. The case: The cargo is handed to a carrier that isn't the verified/assigned one. The solution: Tie pickup to the carrier/driver's verified identity (the same device+face binding as delivery), a pickup PIN shared only with the assignee, and forbid re-brokering without a logged approval. Cross-check the company that actually shows up. And how the tester checks it: Pickup by an unverified carrier → blocked. Without the right PIN → not released. Re-assignment without approval → rejected and audited.


## x38 — Foto de POD manipulada

**ES:** La "prueba de entrega" podría ser una foto vieja o editada. Conviene que la saque la app en el momento y no aceptar cualquier imagen de la galería. El caso: Suben una foto editada o de otra entrega como prueba. La solución: Captura dentro de la app (no upload de galería), con metadatos de tiempo y geo atados server-side, marca de agua/firma de la imagen, y cruce con el geofence y el timestamp de la entrega. La foto es evidencia atada al evento, no un archivo suelto. Y cómo lo prueba el tester: Subir imagen de galería → rechazada / marcada. Foto sin geo/tiempo coherentes con la entrega → flag. Metadata firmada verificable.

**EN (Tampered POD photo):** The "proof of delivery" could be an old or edited photo. Better the app takes it on the spot and doesn't accept any gallery image. The case: An edited photo or one from another delivery is uploaded as proof. The solution: Capture inside the app (no gallery upload), with time and geo metadata bound server-side, image watermark/signature, and cross-check with the delivery's geofence and timestamp. The photo is evidence tied to the event, not a loose file. And how the tester checks it: Upload a gallery image → rejected / flagged. Photo without geo/time consistent with the delivery → flag. Signed, verifiable metadata.


## x39 — Telemetría manipulada (fuel/odómetro)

**ES:** Los datos del camión (kilómetros, combustible, temperatura) podrían inflarse o falsearse para cobrar de más o tapar un problema. Hay que chequear que sean plausibles. El caso: Se reportan litros/km imposibles o retocados para justificar gastos. La solución: Chequeos de plausibilidad (consumo por km dentro de rango, saltos imposibles), cruce con fuentes independientes (GPS vs odómetro, telemetría del proveedor) y datos de sensor firmados donde se pueda. Los outliers van a revisión, no a pago automático. Y cómo lo prueba el tester: Consumo fuera de rango → flag. Salto de odómetro imposible → alerta. GPS vs km reportados incoherentes → revisión.

**EN (Tampered telemetry (fuel/odometer)):** Truck data (mileage, fuel, temperature) could be inflated or faked to overcharge or hide a problem. You must check it's plausible. The case: Impossible or doctored liters/km are reported to justify expenses. The solution: Plausibility checks (consumption per km in range, impossible jumps), cross-check with independent sources (GPS vs odometer, provider telemetry) and signed sensor data where possible. Outliers go to review, not to auto-pay. And how the tester checks it: Consumption out of range → flag. Impossible odometer jump → alert. GPS vs reported km inconsistent → review.


## x40 — Manipulación de precio (client-side)

**ES:** El precio o el total no se puede confiar a lo que manda la pantalla: alguien podría cambiar el número antes de enviarlo. El servidor recalcula todo. El caso: Se altera el precio/total en la request para pagar menos o facturar de más. La solución: El servidor recalcula precios y totales desde la tarifa y los tramos de origen; nunca acepta el monto que manda el cliente. Validación de rangos, moneda y redondeo bancario en un solo lugar auditado. El cliente propone, el servidor decide. Y cómo lo prueba el tester: Enviar total manipulado → el server lo ignora y recalcula. Precio negativo/fuera de rango → 422. Total = suma de tramos server-side.

**EN (Price tampering (client-side)):** The price or total can't be trusted to what the screen sends: someone could change the number before submitting. The server recomputes everything. The case: The price/total is altered in the request to pay less or over-bill. The solution: The server recomputes prices and totals from the tariff and source legs; it never accepts the client-sent amount. Range, currency and banker's-rounding validation in one audited place. The client proposes, the server decides. And how the tester checks it: Send a tampered total → the server ignores it and recomputes. Negative/out-of-range price → 422. Total = sum of legs server-side.


## x41 — Cantidades negativas / abuso de cupones

**ES:** Números que no deberían existir —una cantidad negativa, un descuento aplicado mil veces— pueden regalar plata si nadie los valida. El caso: Cantidad negativa que invierte un cobro, o un cupón reutilizado sin límite. La solución: Validación de dominio en el servidor: cantidades > 0, límites por rango, cupones de un solo uso y por cliente, y reglas de negocio que no se puedan saltar desde la API. Property tests sobre los invariantes económicos. Y cómo lo prueba el tester: Cantidad negativa → 422. Cupón reusado → rechazado. Descuento que deja total < 0 → bloqueado.

**EN (Negative quantities / coupon abuse):** Numbers that shouldn't exist —a negative quantity, a discount applied a thousand times— can give away money if nobody validates them. The case: A negative quantity that reverses a charge, or a coupon reused with no limit. The solution: Server-side domain validation: quantities > 0, range limits, single-use per-customer coupons, and business rules that can't be bypassed from the API. Property tests over the economic invariants. And how the tester checks it: Negative quantity → 422. Reused coupon → rejected. Discount driving total < 0 → blocked.


## x42 — Cadena de frío falsificada

**ES:** En cargas que necesitan frío, alguien podría falsear la temperatura para que parezca que todo estuvo bien. Los datos del sensor tienen que ser confiables. El caso: Se reporta temperatura en rango cuando en realidad se rompió la cadena de frío. La solución: Datos de sensor firmados en origen (device attestation), ingesta idempotente y a prueba de gaps, detección de lagunas sospechosas (silencio = alerta, no "todo ok") y alarma inmediata al salir de rango. La excepción de cold-chain dispara sub-alertas. Y cómo lo prueba el tester: Serie con hueco de datos → alerta, no "ok". Lectura fuera de rango → excepción. Dato de sensor sin firma válida → descartado.

**EN (Falsified cold chain):** On loads needing cold, someone could fake the temperature to make it look fine. The sensor data must be trustworthy. The case: In-range temperature is reported when the cold chain was actually broken. The solution: Origin-signed sensor data (device attestation), idempotent and gap-aware ingestion, detection of suspicious gaps (silence = alert, not "all fine") and an immediate alarm on going out of range. The cold-chain exception fires sub-alerts. And how the tester checks it: Series with a data gap → alert, not "ok". Out-of-range reading → exception. Sensor datum without a valid signature → discarded.


## x43 — DoS / agotamiento de recursos

**ES:** Si alguien manda consultas carísimas o payloads enormes, puede tumbar el sistema para todos. Hay que poner topes. El caso: Requests pesadas o gigantes saturan CPU/memoria y caen el servicio. La solución: Rate limiting, límite de tamaño de payload, paginación con tope máximo (no "traé todo"), timeouts de query y circuit breakers. Trabajos pesados van a cola async. El costo de una request está acotado por diseño. Y cómo lo prueba el tester: Payload sobre el límite → 413. page_size enorme → capado. Query cara → timeout controlado. Aluvión → 429.

**EN (DoS / resource exhaustion):** If someone sends very expensive queries or huge payloads, they can take the system down for everyone. You must set caps. The case: Heavy or giant requests saturate CPU/memory and crash the service. The solution: Rate limiting, payload size limit, pagination with a hard cap (no "give me everything"), query timeouts and circuit breakers. Heavy jobs go to an async queue. A request's cost is bounded by design. And how the tester checks it: Payload over the limit → 413. Huge page_size → capped. Expensive query → controlled timeout. Flood → 429.


## x44 — ReDoS (regex que cuelga)

**ES:** Una expresión regular mal hecha puede tardar eternidades con cierto texto y colgar el servidor con una sola request. El caso: Un input diseñado hace explotar el tiempo de una validación por regex. La solución: Evitar regex con backtracking catastrófico, usar motores/librerías lineales o timeouts de evaluación, límites de longitud de entrada y validaciones simples cuando alcanza. Revisar los patrones que tocan input del usuario. Y cómo lo prueba el tester: Input malicioso contra la regex → tiempo acotado, no cuelga. Fuzzing de validaciones. Longitud de entrada limitada.

**EN (ReDoS (hanging regex)):** A badly written regular expression can take forever on certain text and hang the server with a single request. The case: A crafted input blows up the time of a regex validation. The solution: Avoid regex with catastrophic backtracking, use linear engines/libraries or evaluation timeouts, input-length limits and simple validations when they suffice. Review patterns touching user input. And how the tester checks it: Malicious input against the regex → bounded time, doesn't hang. Fuzz validations. Input length limited.


## x45 — Mass assignment (overposting)

**ES:** Al crear o editar algo, el usuario no puede colar campos que no le tocan (como su rol, el tenant o "está pago") mandándolos en el JSON. El caso: Agregar role:admin o tenant_id al body y que el server lo acepte. La solución: Allowlist explícita de campos vinculables (DTO de entrada), nunca bindear el body directo al modelo. Los campos sensibles (rol, tenant, estado de pago) se setean server-side, no desde la request. Lo no esperado se ignora. Y cómo lo prueba el tester: Body con role/tenant/flags extra → ignorados, no aplican. Solo campos permitidos se persisten. Intento de override → sin efecto.

**EN (Mass assignment (overposting)):** When creating or editing, the user can't slip in fields that aren't theirs (like their role, the tenant or "is paid") by sending them in the JSON. The case: Add role:admin or tenant_id to the body and have the server accept it. The solution: Explicit allowlist of bindable fields (input DTO), never bind the body directly to the model. Sensitive fields (role, tenant, payment status) are set server-side, not from the request. The unexpected is ignored. And how the tester checks it: Body with extra role/tenant/flags → ignored, don't apply. Only allowed fields persist. Override attempt → no effect.


## x46 — Race condition / TOCTOU (doble reserva)

**ES:** Si dos pedidos toman el último lugar del camión al mismo tiempo, no puede quedar sobrevendido. El chequeo y la reserva tienen que ser una sola cosa. El caso: Dos requests simultáneas reservan la misma capacidad (o el mismo cupón) dos veces. La solución: Verificar-y-reservar de forma atómica (transacción + bloqueo, optimista o SELECT ... FOR UPDATE), o una restricción única que impida el doble uso. Nunca "chequeo, y después escribo" con una ventana en el medio. Bajo carga, una gana (409) y la otra reintenta. Y cómo lo prueba el tester: 2 reservas en paralelo sobre 1 cupo → una 200, otra 409. Sin sobreventa. Cupón único usado 2× → rechazo.

**EN (Race condition / TOCTOU (double booking)):** If two orders grab the last slot in the truck at once, it can't end up oversold. The check and the reservation must be one thing. The case: Two simultaneous requests reserve the same capacity (or coupon) twice. The solution: Check-and-reserve atomically (transaction + lock, optimistic or SELECT ... FOR UPDATE), or a unique constraint that forbids double use. Never "check, then write" with a window in between. Under load, one wins (409) and the other retries. And how the tester checks it: 2 parallel reservations on 1 slot → one 200, one 409. No oversell. Single coupon used 2× → reject.


## x47 — Envenenamiento de cola/webhook

**ES:** Un mensaje malformado o venenoso en la cola no puede frenar toda la fila ni procesarse infinitas veces. Hay que aislarlo. El caso: Un mensaje inválido bloquea el consumidor o se reintenta para siempre. La solución: Validación de schema a la entrada, límite de reintentos con dead-letter queue para los que fallan, idempotencia por id y poison-message handling para no atascar la cola. Un mensaje malo se aísla, se alerta y el resto sigue. Y cómo lo prueba el tester: Mensaje inválido → va a DLQ, no frena la cola. Reintentos acotados. Mismo id 2× → 1 efecto.

**EN (Queue/webhook poisoning):** A malformed or poison message in the queue can't stall the whole line or be processed infinitely. You must isolate it. The case: An invalid message blocks the consumer or is retried forever. The solution: Schema validation at intake, a retry limit with a dead-letter queue for failures, idempotency by id and poison-message handling so the queue doesn't jam. A bad message is isolated, alerted, and the rest proceeds. And how the tester checks it: Invalid message → goes to DLQ, doesn't stall the queue. Bounded retries. Same id 2× → 1 effect.


## x48 — Dispositivo rooteado / con jailbreak

**ES:** Un teléfono "liberado" (rooteado) es más fácil de manipular: se pueden falsear GPS, cámara o datos. Para operaciones sensibles conviene desconfiar de esos equipos. El caso: La app corre en un device comprometido que falsea sensores y almacenamiento. La solución: Device attestation (Play Integrity / DeviceCheck) que verifica que el equipo y la app son legítimos; en dispositivos comprometidos se limita o niega la confirmación de entrega y se pide verificación reforzada. La decisión se valida server-side. Y cómo lo prueba el tester: Device rooteado/emulador → atestación falla → entrega bloqueada o step-up. La app no confía en su propio "estoy sano".

**EN (Rooted / jailbroken device):** A "freed" (rooted) phone is easier to manipulate: GPS, camera or data can be faked. For sensitive operations, distrust such devices. The case: The app runs on a compromised device that fakes sensors and storage. The solution: Device attestation (Play Integrity / DeviceCheck) verifying the device and app are legit; on compromised devices, delivery confirmation is limited or denied and stronger verification is required. The decision is validated server-side. And how the tester checks it: Rooted device/emulator → attestation fails → delivery blocked or step-up. The app doesn't trust its own "I'm healthy".


## x49 — App manipulada / repackaged

**ES:** Alguien puede tomar la app, modificarla y publicar una versión trucha que se saltea controles. El backend tiene que reconocer solo a la app legítima. El caso: Una app repackaged con validaciones removidas opera contra la API real. La solución: Attestation de integridad de la app, verificación de firma del binario, ofuscación y controles anti-tamper, y —clave— no depender de controles del cliente: toda regla crítica se valida en el servidor. Una app modificada no debería lograr nada que el server no permita igual. Y cómo lo prueba el tester: App con firma/hash no oficial → atestación falla. Saltar una validación del cliente → el server igual rechaza. Controles críticos server-side.

**EN (Tampered / repackaged app):** Someone can take the app, modify it and publish a fake version that skips controls. The backend must recognize only the legit app. The case: A repackaged app with validations removed operates against the real API. The solution: App integrity attestation, binary signature verification, obfuscation and anti-tamper controls, and —crucially— don't rely on client-side controls: every critical rule is validated on the server. A modified app shouldn't achieve anything the server wouldn't allow anyway. And how the tester checks it: App with an unofficial signature/hash → attestation fails. Skip a client validation → the server still rejects. Critical controls server-side.


## x50 — Datos sensibles cacheados en el device

**ES:** La app del chofer guarda cosas para trabajar sin señal (PODs, direcciones). Si se pierde el teléfono, eso no puede quedar accesible. El caso: Un teléfono perdido/robado expone datos offline y capturas de pantalla. La solución: Almacenamiento local cifrado (keystore del sistema), borrado al cerrar sesión o tras inactividad, bloqueo de screenshots en pantallas sensibles y nada de PII en logs/clipboard. La caché offline es mínima y con vencimiento. Y cómo lo prueba el tester: Inspeccionar el storage de la app → datos cifrados, no en claro. Logout → caché borrada. Pantalla sensible → screenshot bloqueado.

**EN (Sensitive data cached on device):** The driver app stores things to work offline (PODs, addresses). If the phone is lost, that can't stay accessible. The case: A lost/stolen phone exposes offline data and screenshots. The solution: Encrypted local storage (system keystore), wipe on logout or after inactivity, screenshot blocking on sensitive screens and no PII in logs/clipboard. The offline cache is minimal and expiring. And how the tester checks it: Inspect the app storage → data encrypted, not in the clear. Logout → cache wiped. Sensitive screen → screenshot blocked.
