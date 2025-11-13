// ==================== 게임 설정 ====================
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// 사운드 설정
const audioContext = new (window.AudioContext || window.webkitAudioContext)();

function playSound(frequency, duration, type = 'sine') {
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = frequency;
    oscillator.type = type;
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + duration);
}

// 게임 상태
let gameState = {
    running: false,
    paused: false,
    gameOver: false,
    score: 0,
    lives: 3,
    level: 1,
    waveCount: 0,
    bulletCount: 1 // 한 번에 발사되는 총알 개수
};

// ==================== 플레이어 ====================
const player = {
    x: canvas.width / 2,
    y: canvas.height - 50,
    width: 30,
    height: 40,
    speed: 5,
    dx: 0,
    bullets: [],
    invulnerableTime: 0,
    invulnerableDuration: 120,
    bulletLevel: 1 // 1, 2, 4, 8 총알 단계
};

// ==================== 적 ====================
let enemies = [];
let enemyBullets = [];
let items = [];

const enemyTypes = {
    small: { width: 20, height: 20, health: 1, speed: 2, score: 10, fruit: 'apple' },
    medium: { width: 30, height: 30, health: 2, speed: 1.5, score: 25, fruit: 'banana' },
    large: { width: 40, height: 40, health: 3, speed: 1, score: 50, fruit: 'orange' },
    boss: { width: 60, height: 60, health: 5, speed: 1, score: 100, fruit: 'cherry' }
};

const fruits = {
    apple: { color: '#FF6B6B', emoji: '🍎' },
    banana: { color: '#FFD93D', emoji: '🍌' },
    orange: { color: '#FF9F43', emoji: '🍊' },
    cherry: { color: '#EE5A6F', emoji: '🍒' },
    med_apple: { color: '#FF4D4D', emoji: '🍎', large: true }
};

// ==================== 파티클 시스템 ====================
let particles = [];
let explosions = [];

// ==================== UI 요소 ====================
const scoreDisplay = document.getElementById('score');
const livesDisplay = document.getElementById('lives');
const levelDisplay = document.getElementById('level');
const gameOverScreen = document.getElementById('gameOverScreen');
const gameWinScreen = document.getElementById('gameWinScreen');
const pauseScreen = document.getElementById('pauseScreen');
const startBtn = document.getElementById('startBtn');
const pauseBtn = document.getElementById('pauseBtn');
const resumeBtn = document.getElementById('resumeBtn');
const resetBtn = document.getElementById('resetBtn');
const retryBtn = document.getElementById('retryBtn');
const nextLevelBtn = document.getElementById('nextLevelBtn');

// ==================== 입력 처리 ====================
const keys = {};

document.addEventListener('keydown', (e) => {
    keys[e.key] = true;
    
    if (e.key === ' ') {
        e.preventDefault();
        if (!gameState.gameOver && !gameState.paused) {
            playerShoot();
        }
    }
});

document.addEventListener('keyup', (e) => {
    keys[e.key] = false;
});

canvas.addEventListener('mousemove', (e) => {
    if (gameState.running && !gameState.paused) {
        const rect = canvas.getBoundingClientRect();
        player.x = e.clientX - rect.left - player.width / 2;
        player.x = Math.max(0, Math.min(canvas.width - player.width, player.x));
    }
});

canvas.addEventListener('click', () => {
    if (gameState.running && !gameState.paused && !gameState.gameOver) {
        playerShoot();
    }
});

// ==================== 버튼 이벤트 ====================
startBtn.addEventListener('click', startGame);
pauseBtn.addEventListener('click', pauseGame);
resumeBtn.addEventListener('click', resumeGame);
resetBtn.addEventListener('click', resetGame);
retryBtn.addEventListener('click', resetGame);
nextLevelBtn.addEventListener('click', nextLevel);

// ==================== 게임 함수 ====================

function startGame() {
    if (!gameState.running) {
        gameState.running = true;
        gameState.paused = false;
        gameState.gameOver = false;
        gameOverScreen.classList.add('hidden');
        gameWinScreen.classList.add('hidden');
        pauseScreen.classList.add('hidden');
        
        // UI 업데이트
        updateUI();
        pauseBtn.classList.remove('hidden');
        startBtn.textContent = '게임 시작됨';
        startBtn.disabled = true;
        
        gameLoop();
    }
}

function pauseGame() {
    if (gameState.running && !gameState.paused) {
        gameState.paused = true;
        pauseScreen.classList.remove('hidden');
        pauseBtn.classList.add('hidden');
        resumeBtn.classList.remove('hidden');
    }
}

function resumeGame() {
    if (gameState.paused) {
        gameState.paused = false;
        pauseScreen.classList.add('hidden');
        pauseBtn.classList.remove('hidden');
        resumeBtn.classList.add('hidden');
        gameLoop();
    }
}

function resetGame() {
    gameState = {
        running: false,
        paused: false,
        gameOver: false,
        score: 0,
        lives: 3,
        level: 1,
        waveCount: 0,
        bulletCount: 1
    };
    
    player.x = canvas.width / 2;
    player.y = canvas.height - 50;
    player.bullets = [];
    player.invulnerableTime = 0;
    player.bulletLevel = 1;
    
    enemies = [];
    enemyBullets = [];
    items = [];
    particles = [];
    explosions = [];
    
    gameOverScreen.classList.add('hidden');
    gameWinScreen.classList.add('hidden');
    pauseScreen.classList.add('hidden');
    
    startBtn.textContent = '게임 시작';
    startBtn.disabled = false;
    pauseBtn.classList.add('hidden');
    resumeBtn.classList.add('hidden');
    
    updateUI();
}

function nextLevel() {
    gameState.level++;
    gameState.waveCount = 0;
    gameWinScreen.classList.add('hidden');
    gameState.running = true;
    gameState.paused = false;
    gameState.gameOver = false;
    
    player.bullets = [];
    enemies = [];
    enemyBullets = [];
    particles = [];
    explosions = [];
    
    updateUI();
    gameLoop();
}

function playerShoot() {
    // 다중 총알 발사
    const angles = [];
    const bulletCount = gameState.bulletCount;
    
    if (bulletCount === 1) {
        angles.push(0);
    } else if (bulletCount === 2) {
        angles.push(-10, 10);
    } else if (bulletCount === 4) {
        angles.push(-15, -5, 5, 15);
    } else if (bulletCount === 8) {
        angles.push(-25, -15, -5, 5, 15, 25, 35, -35);
    }
    
    angles.forEach(angle => {
        const radian = (angle * Math.PI) / 180;
        const bullet = {
            x: player.x + player.width / 2 - 2,
            y: player.y - 10,
            width: 4,
            height: 10,
            speed: 7,
            damage: 1,
            vx: Math.sin(radian) * 2,
            vy: -7
        };
        player.bullets.push(bullet);
    });
    
    playSound(600, 0.1, 'sine');
}

function spawnEnemy() {
    if (gameState.paused || gameState.gameOver) return;
    
    const types = ['small', 'medium', 'large'];
    
    // 더 높은 레벨에서는 더 큰 적을 생성
    let type = types[Math.floor(Math.random() * Math.min(3, gameState.level))];
    
    // 보스 생성 (특정 점수에 도달했을 때)
    if (gameState.score > 500 * gameState.level && Math.random() < 0.05) {
        type = 'boss';
    }
    
    const enemyType = enemyTypes[type];
    const enemy = {
        x: Math.random() * (canvas.width - enemyType.width),
        y: -enemyType.width,
        type: type,
        fruit: enemyType.fruit || 'apple',
        health: enemyType.health,
        maxHealth: enemyType.health,
        width: enemyType.width,
        height: enemyType.height,
        speed: enemyType.speed * (1 + gameState.level * 0.1),
        score: enemyType.score,
        shootTimer: 0,
        shootInterval: Math.random() * 30 + 30
    };
    
    enemies.push(enemy);
}

function updatePlayer() {
    // 움직임
    if (keys['ArrowLeft'] || keys['a']) {
        player.x -= player.speed;
    }
    if (keys['ArrowRight'] || keys['d']) {
        player.x += player.speed;
    }
    
    // 경계 제한
    player.x = Math.max(0, Math.min(canvas.width - player.width, player.x));
    
    // 무적 타이머
    if (player.invulnerableTime > 0) {
        player.invulnerableTime--;
    }
    
    // 총알 업데이트
    for (let i = player.bullets.length - 1; i >= 0; i--) {
        const bullet = player.bullets[i];
        bullet.y += bullet.vy;
        bullet.x += bullet.vx;
        
        if (bullet.y < 0 || bullet.x < 0 || bullet.x > canvas.width) {
            player.bullets.splice(i, 1);
        }
    }
}

function updateEnemies() {
    // 적 생성 빈도 (레벨이 높을수록 자주 생성)
    if (Math.random() < 0.02 * (1 + gameState.level * 0.05)) {
        spawnEnemy();
    }
    
    for (let i = enemies.length - 1; i >= 0; i--) {
        const enemy = enemies[i];
        
        enemy.y += enemy.speed;
        
        // 적 발사
        enemy.shootTimer++;
        if (enemy.shootTimer > enemy.shootInterval) {
            enemyShoot(enemy);
            enemy.shootTimer = 0;
        }
        
        // 화면 밖으로 나간 적 제거
        if (enemy.y > canvas.height) {
            enemies.splice(i, 1);
            continue;
        }
        
        // 플레이어와의 충돌 감지
        if (checkCollision(player, enemy)) {
            if (player.invulnerableTime === 0) {
                gameState.lives--;
                player.invulnerableTime = player.invulnerableDuration;
                createExplosion(player.x + player.width / 2, player.y + player.height / 2, 'red');
                playSound(300, 0.3, 'square');
                
                if (gameState.lives <= 0) {
                    endGame();
                }
            }
        }
    }
}

function updateEnemyBullets() {
    for (let i = enemyBullets.length - 1; i >= 0; i--) {
        const bullet = enemyBullets[i];
        bullet.y += bullet.speed;
        
        if (bullet.y > canvas.height) {
            enemyBullets.splice(i, 1);
            continue;
        }
        
        // 플레이어와의 충돌 감지
        if (checkCollision(player, bullet) && player.invulnerableTime === 0) {
            enemyBullets.splice(i, 1);
            gameState.lives--;
            player.invulnerableTime = player.invulnerableDuration;
            createExplosion(player.x + player.width / 2, player.y + player.height / 2, 'orange');
            playSound(200, 0.2, 'square');
            
            if (gameState.lives <= 0) {
                endGame();
            }
        }
    }
}

function updateItems() {
    for (let i = items.length - 1; i >= 0; i--) {
        const item = items[i];
        item.y += item.speed;
        item.rotation += 0.1;
        
        if (item.y > canvas.height) {
            items.splice(i, 1);
            continue;
        }
        
        // 플레이어와의 충돌 감지
        if (checkCollision(player, item)) {
            // 중형 사과(점수 아이템)
            if (item.effect === 'points') {
                gameState.score += item.point || 50;
                createExplosion(item.x + item.width / 2, item.y + item.height / 2, '#FFD700');
                createParticles(item.x + item.width / 2, item.y + item.height / 2, 20);
                playSound(1200, 0.18, 'sine');
            } else {
                // 기본: 총알 업그레이드 (1->2->4->8)
                gameState.bulletCount = Math.min(gameState.bulletCount * 2, 8);
                player.bulletLevel = Math.log2(gameState.bulletCount) + 1;
                createExplosion(item.x + item.width / 2, item.y + item.height / 2, '#FFD700');
                createParticles(item.x + item.width / 2, item.y + item.height / 2, 15);
                playSound(1000, 0.2, 'sine');
            }
            items.splice(i, 1);
            updateUI();
        }
    }
}

function checkCollision(rect1, rect2) {
    return rect1.x < rect2.x + rect2.width &&
           rect1.x + rect1.width > rect2.x &&
           rect1.y < rect2.y + rect2.height &&
           rect1.y + rect1.height > rect2.y;
}

function checkBulletCollisions() {
    for (let i = player.bullets.length - 1; i >= 0; i--) {
        const bullet = player.bullets[i];
        
        for (let j = enemies.length - 1; j >= 0; j--) {
            const enemy = enemies[j];
            
            if (checkCollision(bullet, enemy)) {
                enemy.health -= bullet.damage;
                player.bullets.splice(i, 1);
                
                if (enemy.health <= 0) {
                    gameState.score += enemy.score;
                    createExplosion(enemy.x + enemy.width / 2, enemy.y + enemy.height / 2, 'yellow');
                    createParticles(enemy.x + enemy.width / 2, enemy.y + enemy.height / 2, 10);
                    playSound(800, 0.15, 'sine');
                    
                    // 아이템 드롭 (30% 확률)
                    if (Math.random() < 0.3) {
                        dropItem(enemy);
                    }
                    
                    enemies.splice(j, 1);
                }
                break;
            }
        }
    }
}

function enemyShoot(enemy) {
    const bullet = {
        x: enemy.x + enemy.width / 2 - 2,
        y: enemy.y + enemy.height,
        width: 4,
        height: 8,
        speed: 3 + gameState.level * 0.5
    };
    enemyBullets.push(bullet);
}

function dropItem(enemy) {
    // 기본 아이템은 적의 과일을 따름. 하지만 중형 적은 '중형 사과' 점수 아이템을 드롭
    let fruit = enemy.fruit;
    let effect = 'power';
    let point = 0;

    if (enemy.type === 'medium') {
        fruit = 'med_apple';
        effect = 'points';
        point = 50;
    }

    const item = {
        x: enemy.x + enemy.width / 2 - 15,
        y: enemy.y,
        width: 36,
        height: 36,
        speed: 2,
        rotation: 0,
        type: enemy.type,
        fruit: fruit,
        effect: effect,
        point: point
    };
    items.push(item);
}

function createExplosion(x, y, color = 'yellow') {
    explosions.push({
        x: x,
        y: y,
        radius: 0,
        maxRadius: 30,
        color: color,
        life: 30
    });
}

function createParticles(x, y, count) {
    for (let i = 0; i < count; i++) {
        const angle = (Math.PI * 2 / count) * i;
        const speed = Math.random() * 3 + 2;
        
        particles.push({
            x: x,
            y: y,
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed,
            life: 30,
            color: `hsl(${Math.random() * 60 + 30}, 100%, 50%)`
        });
    }
}

function updateParticles() {
    for (let i = particles.length - 1; i >= 0; i--) {
        const particle = particles[i];
        particle.x += particle.vx;
        particle.y += particle.vy;
        particle.vy += 0.1; // 중력
        particle.life--;
        
        if (particle.life <= 0) {
            particles.splice(i, 1);
        }
    }
}

function updateExplosions() {
    for (let i = explosions.length - 1; i >= 0; i--) {
        const explosion = explosions[i];
        explosion.radius += 2;
        explosion.life--;
        
        if (explosion.life <= 0) {
            explosions.splice(i, 1);
        }
    }
}

function updateUI() {
    scoreDisplay.textContent = gameState.score;
    livesDisplay.textContent = gameState.lives;
    levelDisplay.textContent = gameState.level;
}

function checkLevelCompletion() {
    // 특정 점수에 도달하면 레벨 통과
    if (gameState.score >= 1000 * gameState.level && enemies.length === 0) {
        gameState.running = false;
        gameWinScreen.classList.remove('hidden');
        document.getElementById('winScore').textContent = gameState.score;
    }
}

function endGame() {
    gameState.running = false;
    gameState.gameOver = true;
    gameOverScreen.classList.remove('hidden');
    document.getElementById('finalScore').textContent = gameState.score;
    document.getElementById('finalLevel').textContent = gameState.level;
}

// ==================== 렌더링 ====================
function drawPlayer() {
    // 무적 상태 깜빡임
    if (player.invulnerableTime > 0 && Math.floor(player.invulnerableTime / 5) % 2 === 0) {
        ctx.globalAlpha = 0.5;
    }
    
    ctx.save();
    ctx.translate(player.x + player.width / 2, player.y + player.height / 2);
    
    // 비행기 몸 (주황색 삼각형)
    ctx.fillStyle = '#FF8C00';
    ctx.beginPath();
    ctx.moveTo(0, -15); // 위쪽 끝 (코)
    ctx.lineTo(-10, 15); // 왼쪽 아래
    ctx.lineTo(10, 15); // 오른쪽 아래
    ctx.closePath();
    ctx.fill();
    
    // 비행기 캐노피 (밝은 파란색)
    ctx.fillStyle = '#87CEEB';
    ctx.beginPath();
    ctx.arc(0, -5, 5, 0, Math.PI * 2);
    ctx.fill();
    
    // 비행기 날개 (회색)
    ctx.fillStyle = '#A9A9A9';
    ctx.fillRect(-12, -2, 24, 4);
    
    // 총구 (빨강)
    ctx.fillStyle = '#FF0000';
    ctx.fillRect(-2, -18, 4, 4);
    
    ctx.restore();
    ctx.globalAlpha = 1.0;
}

function drawEnemies() {
    for (const enemy of enemies) {
        ctx.save();
        ctx.translate(enemy.x + enemy.width / 2, enemy.y + enemy.height / 2);
        
        const fruitInfo = fruits[enemy.fruit];
        
        // 과일 모양 그리기
        switch(enemy.fruit) {
            case 'apple':
                // 사과 (빨강)
                ctx.fillStyle = '#FF6B6B';
                ctx.beginPath();
                ctx.arc(0, 0, enemy.width / 2 - 2, 0, Math.PI * 2);
                ctx.fill();
                // 사과 꼭지
                ctx.fillStyle = '#8B4513';
                ctx.fillRect(-1, -10, 2, 5);
                ctx.fillStyle = '#228B22';
                ctx.beginPath();
                ctx.ellipse(5, -8, 4, 2, Math.PI / 4, 0, Math.PI * 2);
                ctx.fill();
                break;
                
            case 'banana':
                // 바나나 (노랑)
                ctx.fillStyle = '#FFD93D';
                ctx.beginPath();
                ctx.arc(-3, 0, enemy.width / 2.5, 0, Math.PI * 2);
                ctx.arc(0, -5, enemy.width / 2.8, 0, Math.PI * 2);
                ctx.arc(3, 0, enemy.width / 2.5, 0, Math.PI * 2);
                ctx.fill();
                // 바나나 밑부분
                ctx.fillStyle = '#DAA520';
                ctx.fillRect(-2, 5, 4, 3);
                break;
                
            case 'orange':
                // 오렌지 (주황)
                ctx.fillStyle = '#FF9F43';
                ctx.beginPath();
                ctx.arc(0, 0, enemy.width / 2 - 1, 0, Math.PI * 2);
                ctx.fill();
                // 오렌지 줄무늬
                ctx.strokeStyle = '#FF8C00';
                ctx.lineWidth = 1;
                for (let i = -1; i <= 1; i++) {
                    ctx.beginPath();
                    ctx.arc(0, 0, (enemy.width / 2 - 1) * (0.6 + i * 0.2), 0, Math.PI * 2);
                    ctx.stroke();
                }
                break;
                
            case 'cherry':
                // 체리 (빨강)
                ctx.fillStyle = '#EE5A6F';
                ctx.beginPath();
                ctx.arc(-5, 0, enemy.width / 3, 0, Math.PI * 2);
                ctx.arc(5, 0, enemy.width / 3, 0, Math.PI * 2);
                ctx.fill();
                // 줄기
                ctx.strokeStyle = '#8B4513';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(-5, -5);
                ctx.lineTo(0, -8);
                ctx.lineTo(5, -5);
                ctx.stroke();
                break;
        }
        
        // 체력 바
        ctx.restore();
        if (enemy.health < enemy.maxHealth) {
            ctx.fillStyle = '#ff0000';
            ctx.fillRect(enemy.x, enemy.y - 5, enemy.width, 3);
            ctx.fillStyle = '#00ff00';
            ctx.fillRect(enemy.x, enemy.y - 5, (enemy.health / enemy.maxHealth) * enemy.width, 3);
        }
    }
}

function drawBullets() {
    // 플레이어 총알
    ctx.fillStyle = '#ffff00';
    for (const bullet of player.bullets) {
        ctx.fillRect(bullet.x, bullet.y, bullet.width, bullet.height);
    }
    
    // 적 총알
    ctx.fillStyle = '#ff6666';
    for (const bullet of enemyBullets) {
        ctx.fillRect(bullet.x, bullet.y, bullet.width, bullet.height);
    }
}

function drawItems() {
    for (const item of items) {
        ctx.save();
        ctx.translate(item.x + item.width / 2, item.y + item.height / 2);
        ctx.rotate(item.rotation);
        
        const fruitInfo = fruits[item.fruit];
        
        // 아이템 과일 그리기
        switch(item.fruit) {
            case 'apple':
                ctx.fillStyle = '#FF6B6B';
                ctx.beginPath();
                ctx.arc(0, 0, 12, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#8B4513';
                ctx.fillRect(-1, -14, 2, 4);
                ctx.fillStyle = '#228B22';
                ctx.beginPath();
                ctx.ellipse(5, -10, 3, 1.5, Math.PI / 4, 0, Math.PI * 2);
                ctx.fill();
                break;
                
            case 'banana':
                ctx.fillStyle = '#FFD93D';
                ctx.beginPath();
                ctx.arc(-3, 0, 10, 0, Math.PI * 2);
                ctx.arc(0, -5, 10, 0, Math.PI * 2);
                ctx.arc(3, 0, 10, 0, Math.PI * 2);
                ctx.fill();
                break;
                
            case 'orange':
                ctx.fillStyle = '#FF9F43';
                ctx.beginPath();
                ctx.arc(0, 0, 12, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = '#FF8C00';
                ctx.lineWidth = 1;
                for (let i = -1; i <= 1; i++) {
                    ctx.beginPath();
                    ctx.arc(0, 0, 12 * (0.6 + i * 0.2), 0, Math.PI * 2);
                    ctx.stroke();
                }
                break;
                
            case 'cherry':
                ctx.fillStyle = '#EE5A6F';
                ctx.beginPath();
                ctx.arc(-5, 0, 8, 0, Math.PI * 2);
                ctx.arc(5, 0, 8, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = '#8B4513';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(-5, -6);
                ctx.lineTo(0, -10);
                ctx.lineTo(5, -6);
                ctx.stroke();
                break;
            
            case 'med_apple':
                // 중형 사과 (크고 밝은 색) — 점수 50 아이템
                ctx.fillStyle = '#FF4D4D';
                ctx.beginPath();
                ctx.arc(0, 0, 16, 0, Math.PI * 2);
                ctx.fill();
                // 꼭지와 잎
                ctx.fillStyle = '#8B4513';
                ctx.fillRect(-2, -18, 4, 6);
                ctx.fillStyle = '#228B22';
                ctx.beginPath();
                ctx.ellipse(7, -14, 5, 2.5, Math.PI / 4, 0, Math.PI * 2);
                ctx.fill();
                // 점수 텍스트
                ctx.fillStyle = '#FFFFFF';
                ctx.font = 'bold 12px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('+50', 0, 6);
                break;
        }
        
        ctx.restore();
        
        // 아이템 반짝임 효과
        ctx.globalAlpha = 0.6 + Math.sin(Date.now() * 0.01) * 0.4;
        ctx.fillStyle = '#FFD700';
        ctx.beginPath();
        ctx.arc(item.x + item.width / 2, item.y + item.height / 2, 15, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1.0;
    }
}

function drawParticles() {
    for (const particle of particles) {
        ctx.globalAlpha = particle.life / 30;
        ctx.fillStyle = particle.color;
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, 2, 0, Math.PI * 2);
        ctx.fill();
    }
    ctx.globalAlpha = 1.0;
}

function drawExplosions() {
    for (const explosion of explosions) {
        ctx.globalAlpha = explosion.life / 30;
        ctx.strokeStyle = explosion.color;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(explosion.x, explosion.y, explosion.radius, 0, Math.PI * 2);
        ctx.stroke();
    }
    ctx.globalAlpha = 1.0;
}

function drawGame() {
    // 배경
    ctx.fillStyle = '#001a4d';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // 별 배경
    drawStarfield();
    
    // 게임 객체 그리기
    drawBullets();
    drawEnemies();
    drawItems();
    drawPlayer();
    drawParticles();
    drawExplosions();
    
    // 현재 총알 단계 표시
    ctx.fillStyle = '#FFD700';
    ctx.font = 'bold 12px Arial';
    ctx.fillText(`총알 단계: ${gameState.bulletCount}`, 10, 20);
    ctx.fillText(`총알 수: ${gameState.bulletCount}발`, 10, 35);
    
    // 디버그 정보
    if (gameState.running && !gameState.paused) {
        ctx.fillStyle = '#ffffff';
        ctx.font = '12px Arial';
        ctx.fillText(`Enemies: ${enemies.length}`, 10, 50);
        ctx.fillText(`Bullets: ${player.bullets.length}`, 10, 65);
        ctx.fillText(`Items: ${items.length}`, 10, 80);
    }
}

function drawStarfield() {
    ctx.fillStyle = '#ffffff';
    ctx.globalAlpha = 0.3;
    
    const time = Date.now() * 0.001;
    
    for (let i = 0; i < 50; i++) {
        const x = (i * 73) % canvas.width;
        const y = (i * 53 + time * 50) % canvas.height;
        ctx.beginPath();
        ctx.arc(x, y, 1, 0, Math.PI * 2);
        ctx.fill();
    }
    
    ctx.globalAlpha = 1.0;
}

// ==================== 게임 루프 ====================
function gameLoop() {
    if (!gameState.running || gameState.paused) {
        return;
    }
    
    // 업데이트
    updatePlayer();
    updateEnemies();
    updateEnemyBullets();
    updateItems();
    checkBulletCollisions();
    updateParticles();
    updateExplosions();
    updateUI();
    checkLevelCompletion();
    
    // 렌더링
    drawGame();
    
    requestAnimationFrame(gameLoop);
}

// 초기화
updateUI();
console.log('제비우스 게임 로드됨!');
