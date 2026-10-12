"""Unit tests for Internet Speed Meter components."""
import os
import unittest
from config import ConfigManager, THEMES, DEFAULT_CONFIG
from speed_tracker import (
    format_bytes_speed,
    format_bits_speed,
    format_data_volume,
    SpeedTracker
)
from autostart import is_autostart_enabled, get_launch_command


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.test_config_path = "test_config_temp.json"
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)
        self.cfg = ConfigManager(self.test_config_path)

    def tearDown(self):
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)

    def test_default_values(self):
        self.assertEqual(self.cfg.get("opacity"), 0.90)
        self.assertEqual(self.cfg.get("theme"), "cyber_dark")
        self.assertFalse(self.cfg.get("locked"))

    def test_set_and_save(self):
        self.cfg.set("pos_x", 350)
        self.cfg.set("theme", "matrix_green")

        # Reload from disk
        reloaded = ConfigManager(self.test_config_path)
        self.assertEqual(reloaded.get("pos_x"), 350)
        self.assertEqual(reloaded.get("theme"), "matrix_green")

    def test_theme_colors(self):
        colors = self.cfg.get_theme_colors()
        self.assertIn("bg", colors)
        self.assertIn("dl_color", colors)
        self.assertIn("ul_color", colors)


class TestSpeedTracker(unittest.TestCase):
    def test_format_bytes_speed(self):
        val, unit = format_bytes_speed(500)
        self.assertEqual(val, "500")
        self.assertEqual(unit, "B/s")

        val, unit = format_bytes_speed(50 * 1024)
        self.assertEqual(val, "50.0")
        self.assertEqual(unit, "KB/s")

        val, unit = format_bytes_speed(15.5 * 1024 * 1024)
        self.assertEqual(val, "15.5")
        self.assertEqual(unit, "MB/s")

        val, unit = format_bytes_speed(2.45 * 1024 * 1024 * 1024)
        self.assertEqual(val, "2.45")
        self.assertEqual(unit, "GB/s")

    def test_format_bits_speed(self):
        val, unit = format_bits_speed(125000)  # 125 KB/s = 1 Mbps
        self.assertEqual(unit, "Mbps")
        self.assertEqual(val, "1.0")

    def test_format_data_volume(self):
        self.assertEqual(format_data_volume(500 * 1024), "500.0 KB")
        self.assertEqual(format_data_volume(250 * 1024 * 1024), "250.0 MB")
        self.assertEqual(format_data_volume(3 * 1024 * 1024 * 1024), "3.00 GB")

    def test_tracker_update(self):
        tracker = SpeedTracker()
        res = tracker.update()
        self.assertIn("dl_bps", res)
        self.assertIn("ul_bps", res)
        formatted = tracker.get_formatted_speeds()
        self.assertIn("dl_val", formatted)
        self.assertIn("ul_val", formatted)


class TestAutostart(unittest.TestCase):
    def test_launch_command(self):
        cmd = get_launch_command()
        self.assertTrue(len(cmd) > 0)
        self.assertTrue("main.py" in cmd or "main.pyw" in cmd or "InternetSpeedMeter.exe" in cmd)


if __name__ == "__main__":
    unittest.main()
