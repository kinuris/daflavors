from django.db import models

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=255, default='DaFlavors')
    site_tagline = models.CharField(max_length=255, default='Exclusive Venues & Event Catering')
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    address = models.TextField()
    
    # Social media links
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    
    # Meta settings
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    # Logo
    logo = models.ImageField(upload_to='site_settings/', null=True, blank=True)
    favicon = models.ImageField(upload_to='site_settings/', null=True, blank=True)
    
    # Commission rates
    commission_rate_venues = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    commission_rate_caterers = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    
    # Footer text
    footer_text = models.TextField(blank=True)
    
    # Single instance enforcement
    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        if SiteSettings.objects.exists() and not self.pk:
            # If a SiteSettings already exists and this is a new instance, don't save
            return
        return super().save(*args, **kwargs)

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.CharField(max_length=50, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'category', 'question']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
    
    def __str__(self):
        return self.question

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='testimonials/', null=True, blank=True)
    testimonial = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5, help_text="Rating out of 5")
    
    # For approval workflow
    is_approved = models.BooleanField(default=False)
    
    # For ordering on frontend
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"Testimonial by {self.name}"
