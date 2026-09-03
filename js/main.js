import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';

// Setup Scene & Camera
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb); // Sky blue

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 1.6, 5); // Player eye height

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

// Lighting
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);

const sunLight = new THREE.DirectionalLight(0xffffff, 0.9);
sunLight.position.set(30, 50, 30);
sunLight.castShadow = true;
scene.add(sunLight);

// Controls (FPS Mouse Look)
const controls = new PointerLockControls(camera, document.body);
document.body.addEventListener('click', () => {
    controls.lock();
});

// Movement Tracking Variables
const moveState = { forward: false, backward: false, left: false, right: false };
const velocity = new THREE.Vector3();
const direction = new THREE.Vector3();

window.addEventListener('keydown', (e) => {
    if (e.code === 'KeyW') moveState.forward = true;
    if (e.code === 'KeyS') moveState.backward = true;
    if (e.code === 'KeyA') moveState.left = true;
    if (e.code === 'KeyD') moveState.right = true;
    
    // Press 'F' to enter car check
    if (e.code === 'KeyF' && carModel) {
        const distance = camera.position.distanceTo(carModel.position);
        if (distance < 5) {
            isDriving = !isDriving;
            document.getElementById('instruction-text').innerText = isDriving ? 
                "Driving Mode ON! Use WASD to steer." : 
                "Walked out of car. Find car and press 'F' to drive!";
        }
    }
});

window.addEventListener('keyup', (e) => {
    if (e.code === 'KeyW') moveState.forward = false;
    if (e.code === 'KeyS') moveState.backward = false;
    if (e.code === 'KeyA') moveState.left = false;
    if (e.code === 'KeyD') moveState.right = false;
});

// Footstep Audio Setup
const footstepAudio = new Audio('https://actions.google.com/sounds/v1/foley/footsteps_concrete.ogg'); // Temporary CDN sound, you can replace with local file
footstepAudio.loop = true;
let isWalking = false;

// Loaders & Game Entities
const loader = new GLTFLoader();
let mapModel, carModel;
let isDriving = false;

// Load startmap1.glb
loader.load('models/startmap1.glb', (gltf) => {
    mapModel = gltf.scene;
    mapModel.traverse((node) => { if (node.isMesh) node.castShadow = true; node.receiveShadow = true; });
    scene.add(mapModel);
}, undefined, (err) => console.error('Map load error:', err));

// Load oldstartcar1.glb
loader.load('models/oldstartcar1.glb', (gltf) => {
    carModel = gltf.scene;
    carModel.position.set(5, 0, -5); // Position car on map
    carModel.scale.set(1.5, 1.5, 1.5);
    scene.add(carModel);
}, undefined, (err) => console.error('Car load error:', err));

// Game Loop / Animation Clock
const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);
    const delta = clock.getDelta();

    if (controls.isLocked) {
        // Handle Movement
        velocity.x -= velocity.x * 10.0 * delta;
        velocity.z -= velocity.z * 10.0 * delta;

        direction.z = Number(moveState.forward) - Number(moveState.backward);
        direction.x = Number(moveState.right) - Number(moveState.left);
        direction.normalize();

        const speed = 10.0;
        if (moveState.forward || moveState.backward) velocity.z -= direction.z * speed * delta;
        if (moveState.left || moveState.right) velocity.x -= direction.x * speed * delta;

        controls.moveRight(-velocity.x * delta);
        controls.moveForward(-velocity.z * delta);

        // Footstep logic
        const moving = moveState.forward || moveState.backward || moveState.left || moveState.right;
        if (moving && !isDriving) {
            if (!isWalking) {
                footstepAudio.play().catch(() => {});
                isWalking = true;
            }
        } else {
            if (isWalking) {
                footstepAudio.pause();
                isWalking = false;
            }
        }
    }

    // If driving, move the car forward when pressing W
    if (isDriving && carModel) {
        if (moveState.forward) carModel.translateZ(0.1);
        if (moveState.backward) carModel.translateZ(-0.05);
        if (moveState.left) carModel.rotation.y += 0.03;
        if (moveState.right) carModel.rotation.y -= 0.03;

        // Attach camera to follow the car while driving
        camera.position.x = carModel.position.x - Math.sin(carModel.rotation.y) * 5;
        camera.position.z = carModel.position.z - Math.cos(carModel.rotation.y) * 5;
        camera.position.y = carModel.position.y + 2;
    }

    renderer.render(scene, camera);
}

animate();

// Handle Window Resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});
