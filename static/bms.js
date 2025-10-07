(function(){
    const api = async (path, opts={})=>{
        const headers = {'Content-Type':'application/json', ...(opts.headers||{})};
        const tok = localStorage.getItem('access');
        if(tok) headers['Authorization'] = `Bearer ${tok}`;
        const res = await fetch(path, {...opts, headers});
        if(!res.ok) throw new Error(await res.text());
        const ct = res.headers.get('content-type')||'';
        return ct.includes('application/json') ? res.json() : res.text();
    };

    // ------- Auth helpers -------
    const auth = {
        get token(){ return localStorage.getItem('access') || ''; },
        get username(){ return localStorage.getItem('username') || ''; },
        save({access, username}){
            if(access) localStorage.setItem('access', access);
            if(username) localStorage.setItem('username', username);
            updateAuthUI();
        },
        clear(){ localStorage.removeItem('access'); localStorage.removeItem('username'); updateAuthUI(); }
    };

    function updateAuthUI(){
        const userSpan = document.getElementById('bms-user');
        const loginBtn = document.getElementById('bms-login-btn');
        const logoutBtn = document.getElementById('bms-logout-btn');
        if(!userSpan || !loginBtn || !logoutBtn) return;
        if(auth.token){
            userSpan.textContent = auth.username ? `Hi, ${auth.username}` : 'Logged in';
            loginBtn.classList.add('d-none');
            logoutBtn.classList.remove('d-none');
        } else {
            userSpan.textContent = '';
            loginBtn.classList.remove('d-none');
            logoutBtn.classList.add('d-none');
        }
    }

    function showAuthModal(){
        const el = document.getElementById('bms-auth-modal');
        if(!el) return;
        const modal = new bootstrap.Modal(el);
        document.getElementById('bms-auth-error').classList.add('d-none');
        document.getElementById('bms-auth-username').value = '';
        document.getElementById('bms-auth-password').value = '';
        modal.show();
    }

	function on(path, handler){
		if(location.pathname === path){ handler(); }
	}

	// Dark mode persistence
	const toggle = ()=>{
		const isDark = localStorage.getItem('bms-dark') === '1';
		document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
		const input = document.getElementById('bms-dark-toggle');
		if(input) input.checked = isDark;
	};
    window.addEventListener('DOMContentLoaded', ()=>{
		toggle();
		const input = document.getElementById('bms-dark-toggle');
		if(input){
			input.addEventListener('change', ()=>{
				localStorage.setItem('bms-dark', input.checked ? '1' : '0');
				toggle();
			});
		}

        // Auth UI wiring
        updateAuthUI();
        const loginBtn = document.getElementById('bms-login-btn');
        const logoutBtn = document.getElementById('bms-logout-btn');
        const signupAction = document.getElementById('bms-signup-action');
        const loginAction = document.getElementById('bms-login-action');
        if(loginBtn) loginBtn.onclick = showAuthModal;
        if(logoutBtn) logoutBtn.onclick = ()=> auth.clear();
        if(signupAction) signupAction.onclick = async ()=>{
            const username = document.getElementById('bms-auth-username').value.trim();
            const password = document.getElementById('bms-auth-password').value;
            const err = document.getElementById('bms-auth-error');
            err.classList.add('d-none');
            try{
                await api('/signup', { method:'POST', body: JSON.stringify({ username, password }) });
                err.classList.remove('d-none');
                err.classList.replace('alert-danger','alert-success');
                err.textContent = 'Signup successful. You can now login.';
            }catch(e){
                err.classList.remove('d-none');
                err.classList.add('alert-danger');
                err.textContent = e.message || 'Signup failed';
            }
        };
        if(loginAction) loginAction.onclick = async ()=>{
            const username = document.getElementById('bms-auth-username').value.trim();
            const password = document.getElementById('bms-auth-password').value;
            const err = document.getElementById('bms-auth-error');
            err.classList.add('d-none');
            try{
                const data = await api('/login', { method:'POST', body: JSON.stringify({ username, password }) });
                auth.save({ access: data.access, username });
                bootstrap.Modal.getInstance(document.getElementById('bms-auth-modal')).hide();
            }catch(e){
                err.classList.remove('d-none');
                err.classList.add('alert-danger');
                err.textContent = e.message || 'Login failed';
            }
        };
	});

	on('/app', async ()=>{
		const grid = document.getElementById('bms-movie-grid');
		const movies = await api('/movies/');
		grid.innerHTML = movies.map(m=>`
			<div class='col-sm-6 col-md-4 col-lg-3'>
				<div class='bms-card'>
					<div class='bms-poster mb-2'></div>
					<div class='fw-semibold'>${m.title}</div>
					<div class='text-muted small mb-2'>${m.duration_minutes} min</div>
					<a class='btn btn-danger bms-btn btn-sm' href='/app/movies/${m.id}'>Book</a>
				</div>
			</div>`).join('');
	});

	on('/app/movies/'+location.pathname.split('/').pop(), async ()=>{
		const parts = location.pathname.split('/');
		const movieId = parts[parts.length-1];
		const showsWrap = document.getElementById('bms-shows');
		const shows = await api(`/movies/${movieId}/shows/`);
		showsWrap.innerHTML = shows.map(s=>`<div class='d-flex align-items-center gap-3 border-bottom py-2'>
			<div class='flex-grow-1'>${new Date(s.date_time).toLocaleString()} — ${s.screen_name}</div>
			<input type='number' min='1' max='${s.total_seats}' value='1' class='form-control form-control-sm' style='width:90px' />
			<button class='btn btn-primary btn-sm'>Book</button>
		</div>`).join('');
        [...showsWrap.querySelectorAll('button')].forEach((btn, idx)=>{
			btn.onclick = async ()=>{
                if(!auth.token){ showAuthModal(); return; }
				const input = showsWrap.querySelectorAll('input')[idx];
				const seat = parseInt(input.value, 10) || 1;
				const showId = shows[idx].id;
				await api(`/shows/${showId}/book/`, { method:'POST', body: JSON.stringify({ seat_number: seat })});
				alert('Booked!');
			};
		});
	});

	on('/app/my-bookings', async ()=>{
        const ul = document.getElementById('bms-my-bookings');
		try {
			const bookings = await api('/my-bookings/');
			ul.innerHTML = bookings.map(b=>`<li class='list-group-item d-flex justify-content-between align-items-center'>
				<span>${b.show.movie.title} — seat ${b.seat_number} — ${b.status}</span>
				<button class='btn btn-outline-danger btn-sm' data-id='${b.id}'>Cancel</button>
			</li>`).join('');
			ul.querySelectorAll('button[data-id]').forEach(btn=>{
				btn.onclick = async ()=>{
					await api(`/bookings/${btn.dataset.id}/cancel/`, { method: 'POST' });
					location.reload();
				};
			});
		} catch (e) {
			ul.innerHTML = '<li class="list-group-item">Login to view bookings.</li>';
		}
	});
})();


