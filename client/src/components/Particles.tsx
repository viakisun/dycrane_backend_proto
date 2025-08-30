import React, { useEffect, useRef } from 'react';
import './Particles.css';

const Particles: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let particles: any[] = [];
    const particleCount = 50;

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    class Particle {
      x: number;
      y: number;
      size: number;
      speedX: number;
      speedY: number;

      constructor() {
        this.x = Math.random() * canvas!.width;
        this.y = Math.random() * canvas!.height;
        this.size = Math.random() * 3 + 1;
        this.speedX = Math.random() * 1 - 0.5;
        this.speedY = Math.random() * 1 - 0.5;
      }
      update() {
        this.x += this.speedX;
        this.y += this.speedY;

        if (this.size > 0.2) this.size -= 0.01;
      }
      draw() {
        ctx!.fillStyle = 'rgba(0, 255, 255, 0.5)';
        ctx!.strokeStyle = 'rgba(0, 255, 255, 0.5)';
        ctx!.lineWidth = 2;
        ctx!.beginPath();
        ctx!.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx!.closePath();
        ctx!.fill();
      }
    }

    function handleParticles() {
      for (let i = 0; i < particles.length; i++) {
        particles[i].update();
        particles[i].draw();

        if (particles[i].size <= 0.3) {
          particles.splice(i, 1);
          i--;
        }
      }
    }

    function animate() {
      ctx!.clearRect(0, 0, canvas!.width, canvas!.height);
      handleParticles();
      requestAnimationFrame(animate);
    }

    function createParticles() {
        for (let i = 0; i < particleCount; i++) {
            particles.push(new Particle());
        }
    }

    createParticles();
    animate();

    const interval = setInterval(() => {
        if(particles.length < particleCount) {
            createParticles();
        }
    }, 1000);


    return () => clearInterval(interval);
  }, []);

  return <canvas ref={canvasRef} className="particle-canvas" />;
};

export default Particles;
