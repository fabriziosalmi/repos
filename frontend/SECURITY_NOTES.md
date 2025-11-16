# Note di Sicurezza Frontend

## Sanificazione Input Utente (Future Features)

Se in futuro verrà implementato input utente (commenti, form, contenuti generati dall'utente), seguire queste best practices per prevenire attacchi XSS:

### Implementazione DOMPurify

1. **Installazione**:
   ```bash
   npm install dompurify
   npm install -D @types/dompurify
   ```

2. **Utilizzo in Vue Components**:
   ```typescript
   import DOMPurify from 'dompurify';

   // Nel component
   const sanitizedContent = DOMPurify.sanitize(userInput, {
     ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p'],
     ALLOWED_ATTR: ['href']
   });
   ```

3. **Rendering sicuro con v-html**:
   ```vue
   <template>
     <!-- ❌ MAI fare questo con input utente non sanificato -->
     <div v-html="userInput"></div>
     
     <!-- ✅ Sempre sanificare prima -->
     <div v-html="sanitizedUserInput"></div>
   </template>

   <script setup lang="ts">
   import DOMPurify from 'dompurify';
   import { computed } from 'vue';

   const userInput = ref('');
   const sanitizedUserInput = computed(() => 
     DOMPurify.sanitize(userInput.value)
   );
   </script>
   ```

4. **Configurazione Raccomandata**:
   ```typescript
   const config = {
     ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li'],
     ALLOWED_ATTR: ['href', 'title', 'target'],
     ALLOW_DATA_ATTR: false,
     SAFE_FOR_TEMPLATES: true,
     RETURN_TRUSTED_TYPE: true
   };

   const clean = DOMPurify.sanitize(dirty, config);
   ```

### Altre Best Practices

- **Validazione lato client E lato server**: La sanificazione client-side è UX, quella server-side è sicurezza
- **Escape automatico**: Vue già fa escape automatico con `{{ }}`, usare v-html solo quando strettamente necessario
- **Content Security Policy**: Già implementata, blocca script inline non autorizzati
- **Rate Limiting**: Implementare su eventuali endpoint API per prevenire spam/abuse

### Riferimenti
- [DOMPurify GitHub](https://github.com/cure53/DOMPurify)
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [Vue.js Security Best Practices](https://vuejs.org/guide/best-practices/security.html)
