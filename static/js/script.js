class SymphonyStudio {
    constructor() {
       
        this.navButtons = document.querySelectorAll('.nav-btn');
        this.modeSections = document.querySelectorAll('.mode-section');
        this.lengthSlider = document.getElementById('poem-length');
        this.lengthValDisplay = document.getElementById('length-val');
        this.generateBtn = document.getElementById('generate-btn');
        this.poemDisplay = document.getElementById('poem-display');
        this.copyBtn = document.getElementById('copy-btn');
        this.seedPool = document.getElementById('seed-word-pool');
        this.activeSeedsContainer = document.getElementById('active-seeds');

        
        this.selectedSeeds = new Set();
        this.activeMode = 'mode-corpus';

        this.init();
    }

    init() {
       
        this.navButtons.forEach(btn => {
            btn.addEventListener('click', () => this.switchMode(btn.dataset.mode));
        });

        
        if (this.lengthSlider) {
            this.lengthSlider.addEventListener('input', () => {
                if (this.lengthValDisplay) {
                    this.lengthValDisplay.textContent = `${this.lengthSlider.value} words`;
                }
            });
        }

        
        if (this.copyBtn) {
            this.copyBtn.addEventListener('click', () => {
                navigator.clipboard.writeText(this.poemDisplay.innerText);
                this.copyBtn.textContent = "Copied!";
                setTimeout(() => this.copyBtn.textContent = "Copy to Clipboard", 2000);
            });
        }

   
        if (this.seedPool) {
            this.seedPool.querySelectorAll('.chip').forEach(chip => {
                chip.onclick = () => this.toggleSeed(chip.textContent, chip);
            });
        }
    }

    switchMode(modeId) {
        this.activeMode = modeId;
        this.navButtons.forEach(b => b.classList.toggle('active', b.dataset.mode === modeId));
        this.modeSections.forEach(s => s.classList.toggle('active', s.id === modeId));

        if (this.generateBtn) {
            this.generateBtn.style.display = modeId === 'mode-interactive' ? 'none' : 'block';
        }
    }

    toggleSeed(word, chip) {
        if (this.selectedSeeds.has(word)) {
            this.selectedSeeds.delete(word);
            chip.classList.remove('active');
        } else {
            this.selectedSeeds.add(word);
            chip.classList.add('active');
        }
        this.renderActiveSeeds();
    }

    renderActiveSeeds() {
        if (!this.activeSeedsContainer) return;
        this.activeSeedsContainer.innerHTML = '';
        this.selectedSeeds.forEach(word => {
            const span = document.createElement('span');
            span.className = 'badge';
            span.textContent = word;
            this.activeSeedsContainer.appendChild(span);
        });
    }


    async animatePoem(lines) {
        this.poemDisplay.innerHTML = '';
        this.copyBtn.classList.remove('invisible');

        for (const line of lines) {
            await this.addLine(line);
        }
    }

    addLine(text) {
        return new Promise(r => {
            const p = document.createElement('p');
            p.textContent = text;
            p.className = 'poem-line'; 
            p.style.opacity = '0';
            p.style.transform = 'translateY(10px)';
            p.style.transition = 'all 0.5s ease';

            this.poemDisplay.appendChild(p);

            requestAnimationFrame(() => {
                p.style.opacity = '1';
                p.style.transform = 'translateY(0)';
            });
            setTimeout(r, 400); 
        });
    }
}


document.addEventListener('DOMContentLoaded', () => {
    window.symphony = new SymphonyStudio();
});