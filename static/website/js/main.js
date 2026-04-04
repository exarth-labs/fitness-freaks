// Fitness Freaks - Interactive JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // ===== Scroll Animations =====
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-slide-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
    
    // ===== Navbar Scroll Effect =====
    const navbar = document.querySelector('.nav-modern');
    let lastScroll = 0;
    
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 100) {
            navbar.classList.add('scrolled');
            navbar.style.background = 'rgba(10, 10, 15, 0.95)';
        } else {
            navbar.classList.remove('scrolled');
            navbar.style.background = 'rgba(10, 10, 15, 0.8)';
        }
        
        lastScroll = currentScroll;
    });
    
    // ===== Counter Animation =====
    const animateCounter = (element, target, duration = 2000) => {
        const start = 0;
        const increment = target / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                element.textContent = target.toLocaleString();
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current).toLocaleString();
            }
        }, 16);
    };
    
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = parseInt(entry.target.getAttribute('data-target'));
                animateCounter(entry.target, target);
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    document.querySelectorAll('[data-target]').forEach(el => {
        counterObserver.observe(el);
    });
    
    // ===== Smooth Scroll for Anchor Links =====
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // ===== Mobile Menu Toggle =====
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const mobileMenu = document.getElementById('mobileMenu');
    const mobileMenuClose = document.getElementById('mobileMenuClose');
    
    console.log('Mobile menu elements:', { mobileMenuBtn, mobileMenu, mobileMenuClose });

    if (mobileMenuBtn && mobileMenu && mobileMenuClose) {
        mobileMenuBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const currentTransform = mobileMenu.style.transform;
            const isClosed = currentTransform === 'translateX(-100%)' || currentTransform === '';
            console.log('Menu click, isClosed:', isClosed, 'currentTransform:', currentTransform);
            
            if (isClosed) {
                // Open menu
                mobileMenu.style.transform = 'translateX(0)';
                mobileMenuBtn.innerHTML = '<i class="fas fa-times text-2xl"></i>';
                document.body.style.overflow = 'hidden';
            } else {
                // Close menu
                mobileMenu.style.transform = 'translateX(-100%)';
                mobileMenuBtn.innerHTML = '<i class="fas fa-bars text-2xl"></i>';
                document.body.style.overflow = '';
            }
        });

        mobileMenuClose.addEventListener('click', () => {
            mobileMenu.style.transform = 'translateX(-100%)';
            mobileMenuBtn.innerHTML = '<i class="fas fa-bars text-2xl"></i>';
            document.body.style.overflow = '';
        });

        mobileMenu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.style.transform = 'translateX(-100%)';
                mobileMenuBtn.innerHTML = '<i class="fas fa-bars text-2xl"></i>';
                document.body.style.overflow = '';
            });
        });
    } else {
        console.error('Mobile menu elements not found!');
    }
    
    // ===== Parallax Effect for Hero =====
    const hero = document.querySelector('.hero-section');
    if (hero) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const heroContent = hero.querySelector('.hero-content');
            if (heroContent) {
                heroContent.style.transform = `translateY(${scrolled * 0.3}px)`;
                heroContent.style.opacity = 1 - (scrolled / 500);
            }
        });
    }
    
    // ===== Gallery Lightbox =====
    const galleryItems = document.querySelectorAll('.gallery-item');
    const lightbox = document.querySelector('.lightbox');
    
    if (lightbox) {
        galleryItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const img = item.querySelector('img');
                const src = img.getAttribute('src');
                const alt = img.getAttribute('alt');
                
                lightbox.querySelector('img').src = src;
                lightbox.querySelector('figcaption').textContent = alt;
                lightbox.style.display = 'flex';
                setTimeout(() => {
                    lightbox.classList.remove('hidden');
                    lightbox.classList.add('flex');
                }, 10);
                document.body.style.overflow = 'hidden';
            });
        });
        
        lightbox.addEventListener('click', (e) => {
            if (e.target === lightbox || e.target.closest('.lightbox-close')) {
                lightbox.classList.add('hidden');
                lightbox.classList.remove('flex');
                setTimeout(() => {
                    lightbox.style.display = 'none';
                }, 10);
                document.body.style.overflow = '';
            }
        });
        
        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && lightbox.style.display === 'flex') {
                lightbox.classList.add('hidden');
                lightbox.classList.remove('flex');
                setTimeout(() => {
                    lightbox.style.display = 'none';
                }, 10);
                document.body.style.overflow = '';
            }
        });
    }
    
    // ===== Form Validation =====
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const formData = new FormData(contactForm);
            const data = Object.fromEntries(formData);
            
            // Simple validation
            let isValid = true;
            const requiredFields = ['name', 'email', 'message'];
            
            requiredFields.forEach(field => {
                const input = contactForm.querySelector(`[name="${field}"]`);
                if (!data[field] || data[field].trim() === '') {
                    isValid = false;
                    input.classList.add('error');
                } else {
                    input.classList.remove('error');
                }
            });
            
            if (isValid) {
                // Show success message
                const successMsg = document.createElement('div');
                successMsg.className = 'success-message';
                successMsg.innerHTML = `
                    <div class="success-content">
                        <i class="fas fa-check-circle"></i>
                        <p>Message sent successfully! We'll get back to you soon.</p>
                    </div>
                `;
                contactForm.appendChild(successMsg);
                contactForm.reset();
                
                setTimeout(() => {
                    successMsg.remove();
                }, 5000);
            }
        });
    }
    
    // ===== Testimonial Slider =====
    const testimonials = document.querySelectorAll('.testimonial-card');
    let currentTestimonial = 0;
    
    if (testimonials.length > 0) {
        const showTestimonial = (index) => {
            testimonials.forEach((t, i) => {
                t.classList.toggle('active', i === index);
            });
        };
        
        setInterval(() => {
            currentTestimonial = (currentTestimonial + 1) % testimonials.length;
            showTestimonial(currentTestimonial);
        }, 5000);
    }
    
    // ===== Particle Effect =====
    const createParticles = () => {
        const container = document.querySelector('.particles');
        if (!container) return;
        
        for (let i = 0; i < 50; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 15 + 's';
            particle.style.animationDuration = (Math.random() * 10 + 10) + 's';
            container.appendChild(particle);
        }
    };
    
    createParticles();
    
    // ===== Pricing Toggle (Monthly/Yearly) =====
    const pricingToggle = document.querySelector('.pricing-toggle');
    if (pricingToggle) {
        pricingToggle.addEventListener('change', (e) => {
            const isYearly = e.target.checked;
            const prices = document.querySelectorAll('.price-amount');
            
            prices.forEach(price => {
                const monthly = parseInt(price.getAttribute('data-monthly'));
                const yearly = parseInt(price.getAttribute('data-yearly'));
                price.textContent = (isYearly ? yearly : monthly).toLocaleString();
            });
        });
    }
    
    // ===== Typing Effect for Hero =====
    const typingElement = document.querySelector('.typing-text');
    if (typingElement) {
        const texts = typingElement.getAttribute('data-texts').split('|');
        let textIndex = 0;
        let charIndex = 0;
        let isDeleting = false;
        
        const type = () => {
            const currentText = texts[textIndex];
            
            if (isDeleting) {
                typingElement.textContent = currentText.substring(0, charIndex - 1);
                charIndex--;
            } else {
                typingElement.textContent = currentText.substring(0, charIndex + 1);
                charIndex++;
            }
            
            let typeSpeed = isDeleting ? 50 : 100;
            
            if (!isDeleting && charIndex === currentText.length) {
                typeSpeed = 2000;
                isDeleting = true;
            } else if (isDeleting && charIndex === 0) {
                isDeleting = false;
                textIndex = (textIndex + 1) % texts.length;
                typeSpeed = 500;
            }
            
            setTimeout(type, typeSpeed);
        };
        
        type();
    }
    
    // ===== Active Navigation Highlight =====
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link-modern');
    
    window.addEventListener('scroll', () => {
        let current = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (window.pageYOffset >= sectionTop - 200) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    });
    
    // ===== Image Lazy Loading =====
    const lazyImages = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.getAttribute('data-src');
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });
    
    lazyImages.forEach(img => imageObserver.observe(img));
    
    console.log('🏋️ Fitness Freaks - Website Loaded Successfully!');
});
