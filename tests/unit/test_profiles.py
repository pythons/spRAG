import unittest

from dsrag.config.profiles import (
    PROFILE_PRESETS,
    get_profile_preset,
    merge_with_profile_defaults,
)


class TestProfiles(unittest.TestCase):
    def test_get_profile_preset_returns_copy(self):
        preset = get_profile_preset("finance_default")
        preset["chunking_config"]["chunk_size"] = 999
        self.assertNotEqual(PROFILE_PRESETS["finance_default"]["chunking_config"]["chunk_size"], 999)

    def test_get_profile_preset_unknown_raises(self):
        with self.assertRaisesRegex(ValueError, "Unknown profile"):
            get_profile_preset("non_existent_profile")

    def test_merge_with_profile_defaults_user_overrides(self):
        profile_defaults = {"chunk_size": 800, "min_length_for_chunking": 1600}
        user_config = {"chunk_size": 1200}
        merged = merge_with_profile_defaults(profile_defaults, user_config)
        self.assertEqual(merged, {"chunk_size": 1200, "min_length_for_chunking": 1600})


if __name__ == "__main__":
    unittest.main()
