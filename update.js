/* ---------- FOOTBALL (Sportmonks) ---------- */
function fetchFootball(){
  const box = document.getElementById('football-box');
  if(!box) return;
  const today = new Date().toISOString().split('T')[0];
  const endpoint = `https://api.sportmonks.com/v3/football/fixtures?date=${today}&api_token=${SPORTMONT_TOKEN}`;
  fetch(endpoint)
    .then(r => r.json())
    .then(json => {
      const matches = json.data || [];
      if(matches.length === 0){
        box.innerText = 'No matches found for today';
        return;
      }
      box.innerHTML = '';
      matches.slice(0,5).forEach(m => {
        const home = m.localTeam?.data?.name || m.teams?.home?.name || 'Home';
        const away = m.visitorTeam?.data?.name || m.teams?.away?.name || 'Away';
        const status = m.status || m.time_status || '—';
        const time = m.time?.starting_at?.time || m.fixture?.date || 'TBD';
        const row = document.createElement('div');
        row.innerHTML = `<strong>${home}</strong> vs <strong>${away}</strong><br/><small>${time} — ${status}</small>`;
        box.appendChild(row);
      });
    })
    .catch(err => {
      console.warn('Football fetch failed', err);
      box.innerText = 'Football data currently unavailable';
    });
}
