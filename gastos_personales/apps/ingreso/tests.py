from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model # Devuelve modelo de usuario activo configurado en el proyecto
from .models import Ingreso, Fuente
from apps.usuario.models import Moneda

# Create your tests here.
class IngresoTests(TestCase):
    def setUp(self):
        User = get_user_model()
        
        # Crear monedas de prueba
        self.moneda_ars = Moneda.objects.create(moneda='Peso Argentino', abreviatura='ARS')
        self.moneda_usd = Moneda.objects.create(moneda='Dólar Estadounidense', abreviatura='USD')
        
        # Crear usuarios de prueba
        self.user1 = User.objects.create_user(
            username='ludmila',
            email='ludmila@example.com',
            password='12345',
            moneda=self.moneda_ars
        )
        self.user2 = User.objects.create_user(
            username='otro_usuario',
            email='otro@example.com',
            password='12345',
            moneda=self.moneda_usd
        )
        
        # Crear fuentes de ingreso de prueba
        self.fuente_sueldo = Fuente.objects.create(nombre='Sueldo')
        self.fuente_freelance = Fuente.objects.create(nombre='Freelance')

        # Crear algunos ingresos de prueba
        Ingreso.objects.create(
            usuario=self.user1,
            fecha='2024-01-01',
            fuente=self.fuente_sueldo,
            monto=1000,
            moneda=self.moneda_ars,
            descripcion='Sueldo Enero'
        )
        Ingreso.objects.create(
            usuario=self.user1,
            fecha='2024-02-01',
            fuente=self.fuente_freelance,
            monto=1500,
            moneda=self.moneda_ars,
            descripcion='Freelance Febrero'
        )
        Ingreso.objects.create(
            usuario=self.user2,
            fecha='2024-03-01',
            fuente=self.fuente_sueldo,
            monto=3000,
            moneda=self.moneda_usd,
            descripcion='Otro usuario'
        )
        
    def test_ingreso_list_view(self):
        self.client.login(username='ludmila', password='12345')
        response = self.client.get(reverse('ingresos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sueldo Enero')
        self.assertContains(response, 'Freelance Febrero')
        self.assertNotContains(response, 'Otro usuario')

    def test_ingreso_create_view(self):
        self.client.login(username='ludmila', password='12345')
        response = self.client.post(reverse('ingresos_create'), {
            'fecha': '2024-03-01',
            'fuente': self.fuente_sueldo.id,
            'monto': 2000,
            'moneda': self.moneda_ars.id,
            'descripcion': 'Sueldo Marzo'
        })
        # Redirección después de crear
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Ingreso.objects.filter(usuario=self.user1).count(), 3)

    def test_ingreso_update_view(self):
        ingreso = Ingreso.objects.filter(usuario=self.user1).first()
        self.client.login(username='ludmila', password='12345')
        response = self.client.post(reverse('ingresos_update', args=[ingreso.id]), {
            'fecha': ingreso.fecha,
            'fuente': ingreso.fuente.id,
            'monto': 1200,
            'moneda': ingreso.moneda.id,
            'descripcion': ingreso.descripcion
        })
        # Redirección después de actualizar
        self.assertEqual(response.status_code, 302)
        ingreso.refresh_from_db()
        self.assertEqual(ingreso.monto, 1200)

    def test_ingreso_delete_view(self):
        ingreso = Ingreso.objects.filter(usuario=self.user1).first()
        self.client.login(username='ludmila', password='12345')
        response = self.client.post(reverse('ingresos_delete', args=[ingreso.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Ingreso.objects.filter(id=ingreso.id).exists())

    def test_crear_ingreso_asigna_usuario_logueado(self):
        """Verifica que al crear un ingreso se asigna el usuario logueado"""
        self.client.login(username='ludmila', password='12345')
        data = {
            'fecha': '2025-11-12',
            'fuente': self.fuente_sueldo.id,
            'monto': 1500,
            'moneda': self.moneda_ars.id,
            'descripcion': 'Bono extra'
        }
        self.client.post(reverse('ingresos_create'), data)
        nuevo = Ingreso.objects.filter(usuario=self.user1, descripcion='Bono extra').exists()
        self.assertTrue(nuevo)