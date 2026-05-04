from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.usuario.models import Moneda
from apps.categoria.models import Categoria
from apps.gasto.models import Gasto


class GastoTests(TestCase):
    def setUp(self):
        User = get_user_model()

        # Crear monedas
        self.moneda_ars = Moneda.objects.create(moneda='Peso Argentino', abreviatura='ARS')
        self.moneda_usd = Moneda.objects.create(moneda='Dólar Estadounidense', abreviatura='USD')

        # Crear usuarios
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

        # Crear categorías
        self.cat_comida = Categoria.objects.create(nombre='Comida')
        self.cat_transporte = Categoria.objects.create(nombre='Transporte')

        # Crear gastos de prueba
        Gasto.objects.create(
            usuario=self.user1,
            fecha='2024-01-10',
            categoria=self.cat_comida,
            monto=500,
            moneda=self.moneda_ars,
            descripcion='Supermercado'
        )
        Gasto.objects.create(
            usuario=self.user1,
            fecha='2024-02-15',
            categoria=self.cat_transporte,
            monto=800,
            moneda=self.moneda_ars,
            descripcion='Colectivo mensual'
        )
        Gasto.objects.create(
            usuario=self.user2,
            fecha='2024-03-20',
            categoria=self.cat_comida,
            monto=100,
            moneda=self.moneda_usd,
            descripcion='Usuario externo'
        )

    # -------------------------------------------------------
    # LIST VIEW
    # -------------------------------------------------------
    def test_gasto_list_view(self):
        self.client.login(username='ludmila', password='12345')
        response = self.client.get(reverse('gastos'))
        self.assertEqual(response.status_code, 200)

        # Debe ver sus propios gastos
        self.assertContains(response, 'Supermercado')
        self.assertContains(response, 'Colectivo mensual')

        # No debe ver gastos de otros usuarios
        self.assertNotContains(response, 'Usuario externo')

    # -------------------------------------------------------
    # CREATE VIEW
    # -------------------------------------------------------
    def test_gasto_create_view(self):
        self.client.login(username='ludmila', password='12345')

        response = self.client.post(reverse('gastos_create'), {
            'fecha': '2024-03-10',
            'categoria': self.cat_comida.id,
            'monto': 1200,
            'moneda': self.moneda_ars.id,
            'descripcion': 'Cena con amigas'
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Gasto.objects.filter(usuario=self.user1).count(), 3)

    # -------------------------------------------------------
    # UPDATE VIEW
    # -------------------------------------------------------
    def test_gasto_update_view(self):
        gasto = Gasto.objects.filter(usuario=self.user1).first()

        self.client.login(username='ludmila', password='12345')

        response = self.client.post(reverse('gastos_update', args=[gasto.id]), {
            'fecha': gasto.fecha,
            'categoria': gasto.categoria.id,
            'monto': 999,
            'moneda': gasto.moneda.id,
            'descripcion': gasto.descripcion
        })

        self.assertEqual(response.status_code, 302)
        gasto.refresh_from_db()
        self.assertEqual(gasto.monto, 999)

    # -------------------------------------------------------
    # DELETE VIEW
    # -------------------------------------------------------
    def test_gasto_delete_view(self):
        gasto = Gasto.objects.filter(usuario=self.user1).first()

        self.client.login(username='ludmila', password='12345')
        response = self.client.post(reverse('gastos_delete', args=[gasto.id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Gasto.objects.filter(id=gasto.id).exists())

    # -------------------------------------------------------
    # AUTO-SET USER
    # -------------------------------------------------------
    def test_crear_gasto_asigna_usuario_logueado(self):
        """Verifica que al crear un gasto se asigna automáticamente el usuario logueado"""
        self.client.login(username='ludmila', password='12345')

        data = {
            'fecha': '2025-11-12',
            'categoria': self.cat_comida.id,
            'monto': 450,
            'moneda': self.moneda_ars.id,
            'descripcion': 'Compra en Kiosko'
        }

        self.client.post(reverse('gastos_create'), data)

        nuevo_gasto = Gasto.objects.filter(usuario=self.user1, descripcion='Compra en Kiosko').exists()
        self.assertTrue(nuevo_gasto)
