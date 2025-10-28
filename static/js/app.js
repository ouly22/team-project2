const transcript = document.getElementById('transcript');

const message = `Bonjour et bienvenue sur SYMOPLEX !
Tu cherches une solution ? 
Eh bien, tu es exactement au bon endroit.
SYMOPLEX est là pour t’aider à trouver la meilleure réponse, facilement et rapidement.
Alors, prêt ?
Clique sur le bouton « Commencer »
et c’est parti pour cette aventure !.`;

// Machine à écrire
function typewriter(text, speed = 25) {
    transcript.textContent = "";
    let i = 0;
    const interval = setInterval(() => {
        transcript.textContent += text.charAt(i);
        i++;
        if (i >= text.length) clearInterval(interval);
    }, speed);
}

// Lecture vocale
function speak(text) {
    if (!('speechSynthesis' in window)) return;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'fr-FR';
    utterance.rate = 1.05;
    utterance.pitch = 1.0;
    // Dans certains navigateurs, il faut appeler speak() après un petit timeout
    setTimeout(() => {
        window.speechSynthesis.speak(utterance);
    }, 100);
}

// Lancement automatique après 3 secondes
window.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        typewriter(message);
        speak(message);
    }, 1000);
});
