/**
 * PetCare – Main JavaScript
 * Handles: mobile nav, date validation, form submit loading state,
 *          confirm dialogs, flash auto-dismiss, status badges,
 *          URL query pre-select, and smooth scroll reveal animations.
 */

document.addEventListener('DOMContentLoaded', () => {

  /* ── MOBILE NAVIGATION ──────────────────────────────────────────── */
  const menuToggle = document.getElementById('menuToggle');
  const mainNav    = document.getElementById('mainNav');

  if (menuToggle && mainNav) {
    menuToggle.addEventListener('click', () => {
      const isOpen = mainNav.classList.toggle('open');
      menuToggle.classList.toggle('open', isOpen);
      menuToggle.setAttribute('aria-expanded', String(isOpen));
      menuToggle.setAttribute('aria-label', isOpen ? 'Đóng menu' : 'Mở menu');
    });

    // Close nav when a link is clicked
    mainNav.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        mainNav.classList.remove('open');
        menuToggle.classList.remove('open');
        menuToggle.setAttribute('aria-expanded', 'false');
        menuToggle.setAttribute('aria-label', 'Mở menu');
      });
    });

    // Close nav when clicking outside
    document.addEventListener('click', (e) => {
      if (!menuToggle.contains(e.target) && !mainNav.contains(e.target)) {
        mainNav.classList.remove('open');
        menuToggle.classList.remove('open');
        menuToggle.setAttribute('aria-expanded', 'false');
        menuToggle.setAttribute('aria-label', 'Mở menu');
      }
    });
  }

  /* ── DATE INPUT: Chỉ áp dụng cho form đặt lịch của khách hàng ───── */
  const clientBookingDate = document.querySelector('#bookingForm #appointmentDate');
  if (clientBookingDate) {
    const now = new Date();
    const localToday = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
      .toISOString().slice(0, 10);
    clientBookingDate.min = localToday;
    clientBookingDate.addEventListener('change', () => {
      if (clientBookingDate.value && clientBookingDate.value < localToday) {
        clientBookingDate.value = '';
        clientBookingDate.setCustomValidity('Vui lòng chọn ngày từ hôm nay trở đi.');
        clientBookingDate.reportValidity();
      } else {
        clientBookingDate.setCustomValidity('');
      }
    });
  }

  /* ── FORM: Ngăn double-submit chỉ khi form đã pass validation ──── */
  const bookingForm = document.getElementById('bookingForm');
  if (bookingForm) {
    bookingForm.addEventListener('submit', function (event) {
      if (!bookingForm.checkValidity()) {
        return; // Để trình duyệt hiển thị tooltip validation
      }
      const btn     = this.querySelector('#submitBtn');
      const btnText = this.querySelector('.btn-text');
      const btnLoad = this.querySelector('.btn-loading');
      if (btn) {
        btn.disabled = true;
        if (btnText) btnText.hidden = true;
        if (btnLoad) btnLoad.hidden = false;
      }
    });
  }

  /* ── CONFIRM BEFORE DELETE / DESTRUCTIVE ACTION ─────────────────── */
  document.querySelectorAll('form[data-confirm]').forEach(form => {
    form.addEventListener('submit', event => {
      const msg = form.dataset.confirm || 'Bạn có chắc chắn không?';
      if (!window.confirm(msg)) {
        event.preventDefault();
      }
    });
  });

  /* ── STATUS BADGE: apply CSS class based on text content ─────────── */
  document.querySelectorAll('.status').forEach(badge => {
    const text = badge.textContent.trim();
    if (text === 'Đã xác nhận')  badge.classList.add('status-da-xac-nhan');
    if (text === 'Đã hoàn thành') badge.classList.add('status-da-hoan-thanh');
    if (text === 'Đã hủy')       badge.classList.add('status-da-huy');
  });

  /* ── FLASH AUTO-DISMISS ─────────────────────────────────────────── */
  document.querySelectorAll('.flash').forEach(flash => {
    const delay = flash.classList.contains('error') ? 9000 : 6500;
    setTimeout(() => {
      if (flash.isConnected) flash.classList.add('flash-fade');
      setTimeout(() => { if (flash.isConnected) flash.remove(); }, 350);
    }, delay);
  });

  /* ── PRE-SELECT SERVICE FROM URL PARAM ──────────────────────────── */
  const serviceSelect = document.getElementById('serviceSelect');
  if (serviceSelect) {
    const params = new URLSearchParams(window.location.search);
    const svc = params.get('service');
    if (svc) {
      for (const opt of serviceSelect.options) {
        if (opt.value === svc) { opt.selected = true; break; }
      }
    }
  }

  /* ── SCROLL REVEAL ANIMATIONS ────────────────────────────────────── */
  const animTargets = document.querySelectorAll(
    '.service-card, .doctor-card, .process-step, .why-card, .review-card, .mvv-card, .stat-block, .service-detail, .contact-detail, .quick-contact-card'
  );

  if ('IntersectionObserver' in window && animTargets.length > 0) {
    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('reveal-in');
          obs.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.12,
      rootMargin: '0px 0px -40px 0px'
    });

    animTargets.forEach(el => {
      el.classList.add('reveal-init');
      observer.observe(el);
    });
  }

});
