from django.contrib import admin
from .models import Payment, Order, OrderProduct


# Register your models here.
class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0
    fields = ('product', 'quantity', 'product_price', 'ordered')  # Asegúrate de que 'product' esté aquí


class OrderAdmin(admin.ModelAdmin):
    
    def get_products(self, obj):
        products = obj.orderproduct_set.all()  # Obtiene todos los productos relacionados con la orden
        return ", ".join([product.product.product_name for product in products])  # Concatena los nombres de los productos

    get_products.short_description = 'Productos'  # Título de la columna en el admin
    
    list_display = ['order_number', 'full_name', 'phone', 'email', 'city', 'order_total', 'tax', 'status', 'is_ordered', 'created_at', 'get_products']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    list_per_page = 20
    inlines = [OrderProductInline]

    



admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)