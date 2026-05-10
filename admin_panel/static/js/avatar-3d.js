/**
 * KUWERA 3D Avatar Controller
 * Using Three.js for interactive 3D head visualization
 */

class Avatar3D {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.head = null;
        this.isSpeaking = false;
        this.isListening = false;
        this.animationFrame = null;
        
        // Facial features
        this.eyes = null;
        this.mouth = null;
        this.headGroup = null;
        
        // Animation states
        this.mouthOpenAmount = 0;
        this.blinkState = 0;
        this.headRotation = { x: 0, y: 0 };
        
        this.init();
    }
    
    init() {
        if (!this.container) return;
        
        // Scene setup
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x12121a);
        
        // Camera
        this.camera = new THREE.PerspectiveCamera(
            45, 
            this.container.clientWidth / this.container.clientHeight, 
            0.1, 
            1000
        );
        this.camera.position.z = 5;
        this.camera.position.y = 0.2;
        
        // Renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.container.appendChild(this.renderer.domElement);
        
        // Lighting
        this.setupLighting();
        
        // Create avatar
        this.createAvatar();
        
        // Add particles
        this.createParticles();
        
        // Start animation loop
        this.animate();
        
        // Handle resize
        window.addEventListener('resize', () => this.onResize());
        
        // Mouse interaction
        this.setupMouseInteraction();
    }
    
    setupLighting() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
        this.scene.add(ambientLight);
        
        // Main directional light
        const mainLight = new THREE.DirectionalLight(0x00d4ff, 0.8);
        mainLight.position.set(2, 2, 5);
        this.scene.add(mainLight);
        
        // Rim light (purple)
        const rimLight = new THREE.DirectionalLight(0x7b2dff, 0.6);
        rimLight.position.set(-2, 1, -3);
        this.scene.add(rimLight);
        
        // Fill light
        const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
        fillLight.position.set(0, -1, 3);
        this.scene.add(fillLight);
        
        // Point lights for glow effect
        const pointLight1 = new THREE.PointLight(0x00d4ff, 0.5, 10);
        pointLight1.position.set(1, 1, 2);
        this.scene.add(pointLight1);
        
        const pointLight2 = new THREE.PointLight(0x7b2dff, 0.3, 10);
        pointLight2.position.set(-1, -0.5, 2);
        this.scene.add(pointLight2);
    }
    
    createAvatar() {
        this.headGroup = new THREE.Group();
        
        // Materials
        this.skinMaterial = new THREE.MeshPhongMaterial({
            color: 0x2a2a3a,
            shininess: 100,
            specular: 0x444444
        });
        
        this.glowMaterial = new THREE.MeshPhongMaterial({
            color: 0x00d4ff,
            emissive: 0x00d4ff,
            emissiveIntensity: 0.3
        });
        
        this.eyeMaterial = new THREE.MeshPhongMaterial({
            color: 0x00d4ff,
            emissive: 0x00d4ff,
            emissiveIntensity: 0.8
        });
        
        // Head shape (modified sphere for face-like appearance)
        const headGeometry = new THREE.SphereGeometry(1, 32, 32);
        headGeometry.scale(0.9, 1.1, 0.9);
        this.head = new THREE.Mesh(headGeometry, this.skinMaterial);
        this.headGroup.add(this.head);
        
        // Face plate (front detail)
        const faceGeometry = new THREE.SphereGeometry(0.85, 32, 32);
        faceGeometry.scale(0.9, 1, 0.3);
        const facePlate = new THREE.Mesh(faceGeometry, new THREE.MeshPhongMaterial({
            color: 0x1a1a25,
            shininess: 80
        }));
        facePlate.position.z = 0.6;
        facePlate.position.y = 0.1;
        this.headGroup.add(facePlate);
        
        // Eyes
        this.createEyes();
        
        // Mouth
        this.createMouth();
        
        // Neural interface details
        this.createNeuralDetails();
        
        // Holographic ring
        this.createHolographicRing();
        
        this.scene.add(this.headGroup);
    }
    
    createEyes() {
        this.eyes = new THREE.Group();
        
        // Left eye
        const eyeGeometry = new THREE.SphereGeometry(0.15, 16, 16);
        const leftEye = new THREE.Mesh(eyeGeometry, this.eyeMaterial);
        leftEye.position.set(-0.3, 0.15, 0.8);
        
        // Right eye
        const rightEye = new THREE.Mesh(eyeGeometry, this.eyeMaterial);
        rightEye.position.set(0.3, 0.15, 0.8);
        
        // Eye glow rings
        const ringGeometry = new THREE.TorusGeometry(0.18, 0.02, 8, 32);
        const leftRing = new THREE.Mesh(ringGeometry, this.glowMaterial);
        leftRing.position.set(-0.3, 0.15, 0.78);
        
        const rightRing = new THREE.Mesh(ringGeometry, this.glowMaterial);
        rightRing.position.set(0.3, 0.15, 0.78);
        
        this.eyes.add(leftEye, rightEye, leftRing, rightRing);
        this.headGroup.add(this.eyes);
    }
    
    createMouth() {
        // Mouth container
        this.mouth = new THREE.Group();
        
        // Mouth base
        const mouthGeometry = new THREE.CapsuleGeometry(0.25, 0.1, 4, 8);
        mouthGeometry.rotateZ(Math.PI / 2);
        const mouthBase = new THREE.Mesh(mouthGeometry, new THREE.MeshPhongMaterial({
            color: 0x0a0a0f,
            shininess: 60
        }));
        mouthBase.position.set(0, -0.25, 0.82);
        
        // Mouth glow line
        const lineGeometry = new THREE.BoxGeometry(0.4, 0.03, 0.02);
        this.mouthLine = new THREE.Mesh(lineGeometry, this.glowMaterial);
        this.mouthLine.position.set(0, -0.25, 0.84);
        
        this.mouth.add(mouthBase, this.mouthLine);
        this.headGroup.add(this.mouth);
    }
    
    createNeuralDetails() {
        // Neural circuit lines on head
        const circuitMaterial = new THREE.MeshBasicMaterial({
            color: 0x00d4ff,
            transparent: true,
            opacity: 0.4
        });
        
        // Circuit lines
        for (let i = 0; i < 6; i++) {
            const angle = (i / 6) * Math.PI * 2;
            const lineGeometry = new THREE.CylinderGeometry(0.01, 0.01, 0.8, 8);
            const line = new THREE.Mesh(lineGeometry, circuitMaterial);
            line.position.set(
                Math.cos(angle) * 0.7,
                0.5,
                Math.sin(angle) * 0.7
            );
            line.rotation.x = Math.PI / 2;
            line.rotation.z = angle;
            this.headGroup.add(line);
        }
        
        // Glowing nodes
        for (let i = 0; i < 8; i++) {
            const angle = (i / 8) * Math.PI * 2;
            const nodeGeometry = new THREE.SphereGeometry(0.04, 8, 8);
            const node = new THREE.Mesh(nodeGeometry, this.glowMaterial);
            node.position.set(
                Math.cos(angle) * 0.75,
                0.3,
                Math.sin(angle) * 0.75
            );
            this.headGroup.add(node);
        }
    }
    
    createHolographicRing() {
        const ringGeometry = new THREE.TorusGeometry(1.5, 0.02, 16, 100);
        this.holoRing = new THREE.Mesh(ringGeometry, new THREE.MeshBasicMaterial({
            color: 0x00d4ff,
            transparent: true,
            opacity: 0.3
        }));
        this.holoRing.rotation.x = Math.PI / 2;
        this.holoRing.position.y = -0.5;
        this.headGroup.add(this.holoRing);
        
        // Second rotating ring
        const ring2Geometry = new THREE.TorusGeometry(1.8, 0.015, 16, 100);
        this.holoRing2 = new THREE.Mesh(ring2Geometry, new THREE.MeshBasicMaterial({
            color: 0x7b2dff,
            transparent: true,
            opacity: 0.2
        }));
        this.holoRing2.rotation.x = Math.PI / 3;
        this.holoRing2.position.y = -0.3;
        this.headGroup.add(this.holoRing2);
    }
    
    createParticles() {
        const particleCount = 50;
        const particles = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);
        
        for (let i = 0; i < particleCount * 3; i += 3) {
            positions[i] = (Math.random() - 0.5) * 5;
            positions[i + 1] = (Math.random() - 0.5) * 5;
            positions[i + 2] = (Math.random() - 0.5) * 5;
        }
        
        particles.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        
        const particleMaterial = new THREE.PointsMaterial({
            color: 0x00d4ff,
            size: 0.03,
            transparent: true,
            opacity: 0.6
        });
        
        this.particleSystem = new THREE.Points(particles, particleMaterial);
        this.scene.add(this.particleSystem);
    }
    
    setupMouseInteraction() {
        let mouseX = 0;
        let mouseY = 0;
        
        this.container.addEventListener('mousemove', (e) => {
            const rect = this.container.getBoundingClientRect();
            mouseX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
            mouseY = -((e.clientY - rect.top) / rect.height) * 2 + 1;
            
            // Smooth head tracking
            this.targetRotationX = mouseY * 0.3;
            this.targetRotationY = mouseX * 0.3;
        });
        
        this.container.addEventListener('mouseleave', () => {
            this.targetRotationX = 0;
            this.targetRotationY = 0;
        });
        
        this.targetRotationX = 0;
        this.targetRotationY = 0;
    }
    
    speak(text) {
        this.isSpeaking = true;
        
        // Animate mouth based on text length
        const duration = text.length * 50; // 50ms per character
        const startTime = Date.now();
        
        const animateMouth = () => {
            const elapsed = Date.now() - startTime;
            const progress = elapsed / duration;
            
            if (progress < 1) {
                // Random mouth movement for speech simulation
                this.mouthOpenAmount = Math.sin(elapsed * 0.02) * 0.5 + 0.5;
                this.mouthLine.scale.y = 1 + this.mouthOpenAmount * 3;
                requestAnimationFrame(animateMouth);
            } else {
                this.isSpeaking = false;
                this.mouthLine.scale.y = 1;
            }
        };
        
        animateMouth();
        
        // Add chat message
        this.addChatMessage(text, 'ai');
    }
    
    listen() {
        this.isListening = true;
        
        // Visual feedback for listening
        const originalEmissive = this.eyeMaterial.emissiveIntensity;
        this.eyeMaterial.emissiveIntensity = 1;
        
        // Pulse effect
        let pulseCount = 0;
        const pulse = () => {
            if (pulseCount < 20 && this.isListening) {
                this.eyeMaterial.emissiveIntensity = 0.5 + Math.sin(pulseCount) * 0.5;
                pulseCount += 0.5;
                requestAnimationFrame(pulse);
            } else {
                this.isListening = false;
                this.eyeMaterial.emissiveIntensity = originalEmissive;
            }
        };
        
        pulse();
    }
    
    addChatMessage(text, sender) {
        const chatDisplay = document.getElementById('avatar-chat-display');
        if (!chatDisplay) return;
        
        const message = document.createElement('div');
        message.className = `chat-message ${sender}`;
        
        const timestamp = new Date().toLocaleTimeString();
        message.innerHTML = `
            <span class="timestamp">[${sender.toUpperCase()}]</span>
            <span class="text">${text}</span>
        `;
        
        chatDisplay.appendChild(message);
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
    }
    
    animate() {
        this.animationFrame = requestAnimationFrame(() => this.animate());
        
        const time = Date.now() * 0.001;
        
        // Smooth head rotation towards mouse
        if (this.headGroup) {
            this.headGroup.rotation.x += (this.targetRotationX - this.headGroup.rotation.x) * 0.05;
            this.headGroup.rotation.y += (this.targetRotationY - this.headGroup.rotation.y) * 0.05;
            
            // Idle animation (subtle breathing)
            this.headGroup.position.y = Math.sin(time * 0.5) * 0.02;
        }
        
        // Rotate holographic rings
        if (this.holoRing) {
            this.holoRing.rotation.z += 0.005;
            this.holoRing.rotation.x = Math.PI / 2 + Math.sin(time * 0.3) * 0.1;
        }
        
        if (this.holoRing2) {
            this.holoRing2.rotation.z -= 0.003;
            this.holoRing2.rotation.x = Math.PI / 3 + Math.cos(time * 0.4) * 0.1;
        }
        
        // Animate particles
        if (this.particleSystem) {
            this.particleSystem.rotation.y += 0.001;
            const positions = this.particleSystem.geometry.attributes.position.array;
            for (let i = 1; i < positions.length; i += 3) {
                positions[i] += Math.sin(time + positions[i - 1]) * 0.002;
            }
            this.particleSystem.geometry.attributes.position.needsUpdate = true;
        }
        
        // Blink animation
        if (this.eyes && !this.isSpeaking && !this.isListening) {
            if (Math.random() < 0.005) { // Random blink
                this.blink();
            }
        }
        
        this.renderer.render(this.scene, this.camera);
    }
    
    blink() {
        const duration = 150; // ms
        const startTime = Date.now();
        
        const animateBlink = () => {
            const elapsed = Date.now() - startTime;
            const progress = elapsed / duration;
            
            if (progress < 1) {
                // Close then open
                const scale = progress < 0.5 ? 1 - progress * 2 : (progress - 0.5) * 2;
                this.eyes.scale.y = scale;
                requestAnimationFrame(animateBlink);
            } else {
                this.eyes.scale.y = 1;
            }
        };
        
        animateBlink();
    }
    
    onResize() {
        if (!this.camera || !this.renderer || !this.container) return;
        
        this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    }
    
    destroy() {
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }
        if (this.renderer) {
            this.renderer.dispose();
            this.container.removeChild(this.renderer.domElement);
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.avatar3D = new Avatar3D('avatar-3d');
});
