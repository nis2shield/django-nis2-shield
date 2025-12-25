# Security Policy

## Versioni Supportate

| Versione | Supportata |
|----------|------------|
| 0.2.x    | ✅ Sì      |
| 0.1.x    | ⚠️ Solo bug critici |
| < 0.1    | ❌ No      |

## Segnalare una Vulnerabilità

**⚠️ NON aprire issue pubbliche per vulnerabilità di sicurezza.**

Se scopri una vulnerabilità di sicurezza in Django NIS2 Shield:

1. **Email**: Invia una descrizione dettagliata a `security@nis2shield.com`
2. **Oggetto**: `[SECURITY] Django NIS2 Shield - Breve descrizione`
3. **Includi**:
   - Descrizione della vulnerabilità
   - Passi per riprodurla
   - Impatto potenziale
   - Eventuale fix proposto

### Cosa Aspettarsi

| Fase | Tempo |
|------|-------|
| Conferma ricezione | 48 ore |
| Prima valutazione | 7 giorni |
| Fix rilasciato | 30 giorni (dipende dalla gravità) |

### Disclosure Responsabile

- Ti chiediamo di non divulgare pubblicamente la vulnerabilità prima del fix
- Verrai accreditato nel CHANGELOG (se lo desideri)
- Non intraprendiamo azioni legali contro ricercatori in buona fede

## Best Practices per Chi Usa la Libreria

1. **Aggiorna regolarmente**: `pip install --upgrade django-nis2-shield`
2. **Chiavi sicure**: Non usare chiavi di default in produzione
3. **Monitora i log**: I log generati vanno analizzati attivamente
4. **Defense in depth**: Questa libreria è un layer, non una soluzione completa

## Audit di Sicurezza

Questo progetto **non è stato ancora sottoposto ad audit di sicurezza professionale**.

Se sei un esperto di sicurezza e vuoi contribuire con una review, sei il benvenuto! Vedi [CONTRIBUTING.md](CONTRIBUTING.md).

---

*Questa policy è ispirata alle best practice di [security.txt](https://securitytxt.org/).*
