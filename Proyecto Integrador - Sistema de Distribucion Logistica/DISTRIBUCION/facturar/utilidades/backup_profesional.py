"""
Código Crítico - Tercer Semestre Año 2026
Backup profesional - Compresión, rotación, progreso real
"""

import os
import zipfile
import shutil
import threading
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, Qt
from PyQt6.QtWidgets import QProgressDialog, QApplication


class BackupManagerProfesional(QObject):
    """Gestor de backups profesional con compresión y rotación."""
    
    progreso = pyqtSignal(int, int)  # actual, total
    mensaje = pyqtSignal(str)
    finalizado = pyqtSignal(bool, str)
    
    def __init__(self, db_path: str = "distribuidora.db", backup_dir: str = "backups"):
        super().__init__()
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.log_file = os.path.join(backup_dir, "backup_log.json")
        self._crear_directorios()
        self._cargar_log()
    
    def _crear_directorios(self):
        """Crea directorios necesarios."""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            print(f"📁 Directorio de backups creado: {self.backup_dir}")
    
    def _cargar_log(self):
        """Carga el historial de backups."""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    self.log = json.load(f)
            except:
                self.log = []
        else:
            self.log = []
    
    def _guardar_log(self):
        """Guarda el historial de backups."""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.log, f, indent=2, ensure_ascii=False)
    
    def _registrar_backup(self, nombre: str, tamaño: float, exito: bool, error: str = None):
        """Registra un backup en el log."""
        self.log.insert(0, {
            'fecha': datetime.now().isoformat(),
            'nombre': nombre,
            'tamaño_mb': round(tamaño, 2),
            'exito': exito,
            'error': error
        })
        # Mantener solo últimos 100 registros
        self.log = self.log[:100]
        self._guardar_log()
    
    def obtener_tamaño_archivo(self, ruta: str) -> float:
        """Obtiene tamaño del archivo en MB."""
        if os.path.exists(ruta):
            return os.path.getsize(ruta) / (1024 * 1024)
        return 0
    
    def crear_backup_con_progreso(self, parent=None, mostrar_progreso: bool = True) -> Optional[str]:
        """
        Crea backup con barra de progreso.
        Retorna ruta del backup o None si falla.
        """
        if not os.path.exists(self.db_path):
            self.mensaje.emit("❌ Base de datos no encontrada")
            return None
        
        # Preparar diálogo de progreso
        dialog = None
        if mostrar_progreso:
            dialog = QProgressDialog("Creando backup...", "Cancelar", 0, 100, parent)
            dialog.setWindowTitle("Backup en curso")
            dialog.setWindowModality(Qt.WindowModality.ApplicationModal)  # CORREGIDO
            dialog.setMinimumDuration(0)
            dialog.setValue(0)
            dialog.show()
            QApplication.processEvents()
        
        try:
            # Paso 1: Verificar base de datos
            if dialog:
                dialog.setLabelText("🔍 Verificando base de datos...")
                dialog.setValue(10)
                QApplication.processEvents()
                if dialog.wasCanceled():
                    return None
            
            # Paso 2: Crear backup temporal
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}.db"
            temp_db = os.path.join(self.backup_dir, backup_name)
            
            if dialog:
                dialog.setLabelText("📀 Copiando archivo...")
                dialog.setValue(30)
                QApplication.processEvents()
                if dialog.wasCanceled():
                    return None
            
            # Copiar archivo
            shutil.copy2(self.db_path, temp_db)
            
            if dialog:
                dialog.setLabelText("🗜️ Comprimiendo backup...")
                dialog.setValue(60)
                QApplication.processEvents()
                if dialog.wasCanceled():
                    os.remove(temp_db)
                    return None
            
            # Paso 3: Comprimir a ZIP
            zip_name = f"backup_{timestamp}.zip"
            zip_path = os.path.join(self.backup_dir, zip_name)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(temp_db, backup_name)
            
            if dialog:
                dialog.setLabelText("🧹 Limpiando archivos temporales...")
                dialog.setValue(85)
                QApplication.processEvents()
            
            # Eliminar archivo temporal
            os.remove(temp_db)
            
            if dialog:
                dialog.setLabelText("✅ Finalizando...")
                dialog.setValue(95)
                QApplication.processEvents()
            
            # Registrar en log
            tamaño = self.obtener_tamaño_archivo(zip_path)
            self._registrar_backup(zip_name, tamaño, True)
            
            # También guardar como "ultimo_backup.zip" (sobrescribir)
            ultimo_backup = os.path.join(self.backup_dir, "ultimo_backup.zip")
            shutil.copy2(zip_path, ultimo_backup)
            
            if dialog:
                dialog.setValue(100)
                QApplication.processEvents()
                # Cerrar diálogo después de 500ms
                QTimer.singleShot(500, dialog.close)
            
            self.mensaje.emit(f"✅ Backup creado: {zip_name} ({tamaño:.2f} MB)")
            
            # Limpiar backups antiguos
            self.limpiar_backups_antiguos(dias=30)
            
            return zip_path
            
        except Exception as e:
            error_msg = str(e)
            self._registrar_backup(backup_name if 'backup_name' in locals() else "desconocido", 0, False, error_msg)
            self.mensaje.emit(f"❌ Error al crear backup: {error_msg}")
            if dialog:
                dialog.close()
            return None
    
    def restaurar_backup(self, backup_path: str, parent=None) -> bool:
        """
        Restaura una copia de seguridad.
        """
        if not os.path.exists(backup_path):
            self.mensaje.emit("❌ Archivo de backup no encontrado")
            return False
        
        # Crear backup de la base actual antes de restaurar
        self.mensaje.emit("📦 Creando backup de seguridad antes de restaurar...")
        backup_previo = self.crear_backup_con_progreso(parent, mostrar_progreso=False)
        
        try:
            # Determinar si es ZIP o DB directo
            if backup_path.endswith('.zip'):
                import tempfile
                with tempfile.TemporaryDirectory() as tmpdir:
                    with zipfile.ZipFile(backup_path, 'r') as zipf:
                        # Extraer el archivo .db
                        for file in zipf.namelist():
                            if file.endswith('.db'):
                                zipf.extract(file, tmpdir)
                                extracted_db = os.path.join(tmpdir, file)
                                shutil.copy2(extracted_db, self.db_path)
                                break
            else:
                shutil.copy2(backup_path, self.db_path)
            
            self.mensaje.emit("✅ Base de datos restaurada correctamente")
            return True
            
        except Exception as e:
            self.mensaje.emit(f"❌ Error al restaurar: {e}")
            return False
    
    def limpiar_backups_antiguos(self, dias: int = 30):
        """Elimina backups más antiguos de X días."""
        try:
            ahora = datetime.now()
            eliminados = 0
            for archivo in os.listdir(self.backup_dir):
                if archivo.startswith("backup_") and (archivo.endswith(".zip") or archivo.endswith(".db")):
                    if archivo == "ultimo_backup.zip":
                        continue
                    ruta = os.path.join(self.backup_dir, archivo)
                    fecha_modif = datetime.fromtimestamp(os.path.getmtime(ruta))
                    if (ahora - fecha_modif).days > dias:
                        os.remove(ruta)
                        eliminados += 1
                        print(f"🗑️ Backup antiguo eliminado: {archivo}")
            if eliminados > 0:
                print(f"✅ Limpieza completada: {eliminados} backups eliminados")
        except Exception as e:
            print(f"⚠️ Error al limpiar backups: {e}")
    
    def listar_backups(self) -> List[Dict[str, Any]]:
        """Lista todos los backups disponibles con información."""
        backups = []
        try:
            for archivo in os.listdir(self.backup_dir):
                if archivo.startswith("backup_") and archivo.endswith(".zip"):
                    ruta = os.path.join(self.backup_dir, archivo)
                    fecha = datetime.fromtimestamp(os.path.getmtime(ruta))
                    tamaño = os.path.getsize(ruta) / (1024 * 1024)
                    backups.append({
                        'nombre': archivo,
                        'fecha': fecha.strftime("%Y-%m-%d %H:%M:%S"),
                        'tamaño': f"{tamaño:.2f} MB",
                        'ruta': ruta
                    })
            backups.sort(key=lambda x: x['fecha'], reverse=True)
        except Exception as e:
            print(f"⚠️ Error al listar backups: {e}")
        return backups
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas de backups."""
        backups = self.listar_backups()
        exitosos = sum(1 for b in self.log if b.get('exito', False))
        fallidos = sum(1 for b in self.log if not b.get('exito', False))
        
        return {
            'total_backups': len(backups),
            'exitosos': exitosos,
            'fallidos': fallidos,
            'ultimo_backup': backups[0] if backups else None,
            'espacio_total_mb': sum(os.path.getsize(b['ruta']) for b in backups) / (1024 * 1024) if backups else 0
        }


class BackupScheduler:
    """Programador de backups automáticos."""
    
    def __init__(self, backup_manager: BackupManagerProfesional):
        self.backup_manager = backup_manager
        self.timer = None
        self.ejecutando = False
    
    def iniciar(self, hora: int = 3, minuto: int = 0):
        """
        Inicia el programador de backups (ejecuta a la hora especificada).
        Args:
            hora: Hora del día (0-23)
            minuto: Minuto (0-59)
        """
        if self.ejecutando:
            return
        
        self.ejecutando = True
        self._programar_siguiente(hora, minuto)
        print(f"⏰ Backup automático programado para las {hora:02d}:{minuto:02d} hs")
    
    def _programar_siguiente(self, hora: int, minuto: int):
        """Programa el próximo backup."""
        ahora = datetime.now()
        proximo = ahora.replace(hour=hora, minute=minuto, second=0, microsecond=0)
        
        if proximo <= ahora:
            proximo += timedelta(days=1)
        
        segundos_hasta = (proximo - ahora).total_seconds()
        
        self.timer = threading.Timer(segundos_hasta, self._ejecutar_backup, args=[hora, minuto])
        self.timer.daemon = True
        self.timer.start()
        print(f"⏰ Próximo backup en {segundos_hasta/3600:.1f} horas")
    
    def _ejecutar_backup(self, hora: int, minuto: int):
        """Ejecuta el backup y programa el siguiente."""
        print(f"🔄 Ejecutando backup automático - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.backup_manager.crear_backup_con_progreso(mostrar_progreso=False)
        self._programar_siguiente(hora, minuto)
    
    def detener(self):
        """Detiene el programador."""
        self.ejecutando = False
        if self.timer:
            self.timer.cancel()
        print("⏰ Backup automático detenido")