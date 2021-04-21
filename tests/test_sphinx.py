import os.path
import posixpath
import tempfile
import unittest

import sphinx_multiversion

from sphinx_multiversion.sphinx import normalize_version


class VersionInfoTestCase(unittest.TestCase):
    def setUp(self):
        root = tempfile.gettempdir()

        self.versioninfo = sphinx_multiversion.sphinx.VersionInfo(
            app=None,
            context={"pagename": "testpage"},
            metadata={
                "master": {
                    "name": "master",
                    "version": "",
                    "release": "0.2",
                    "is_released": False,
                    "source": "heads",
                    "creatordate": "2020-08-07 07:45:20 -0700",
                    "basedir": os.path.join(root, "master"),
                    "sourcedir": os.path.join(root, "master", "docs"),
                    "outputdir": os.path.join(root, "build", "html", "master"),
                    "confdir": os.path.join(root, "master", "docs"),
                    "docnames": ["testpage", "appendix/faq"],
                    "commit": 0x1233456,
                },
                "v0.1.0": {
                    "name": "v0.1.0",
                    "version": "",
                    "release": "0.1.0",
                    "is_released": True,
                    "source": "tags",
                    "creatordate": "2020-07-16 08:45:20 -0100",
                    "basedir": os.path.join(root, "v0.1.0"),
                    "sourcedir": os.path.join(root, "v0.1.0", "docs"),
                    "outputdir": os.path.join(root, "build", "html", "v0.1.0"),
                    "confdir": os.path.join(root, "v0.1.0", "docs"),
                    "docnames": ["old_testpage", "appendix/faq"],
                    "commit": 0xabcdef1234,
                },
                "branch-with/slash": {
                    "name": "branch-with/slash",
                    "version": "",
                    "release": "0.1.1",
                    "is_released": False,
                    "source": "heads",
                    "creatordate": "2020-08-06 11:53:06 -0400",
                    "basedir": os.path.join(root, "branch-with/slash"),
                    "sourcedir": os.path.join(
                        root, "branch-with/slash", "docs"
                    ),
                    "outputdir": os.path.join(
                        root, "build", "html", "branch-with/slash"
                    ),
                    "confdir": os.path.join(root, "branch-with/slash", "docs"),
                    "docnames": ["testpage"],
                    "commit": 0x1234abcdef,
                },
            },
            current_version_name="master",
        )

    def test_tags_property(self):
        versions = self.versioninfo.tags
        self.assertEqual([version.name for version in versions], ["v0.1.0"])

    def test_branches_property(self):
        versions = self.versioninfo.branches
        self.assertEqual(
            [version.name for version in versions],
            ["branch-with/slash", "master"],
        )

    def test_releases_property(self):
        versions = self.versioninfo.releases
        self.assertEqual([version.name for version in versions], ["v0.1.0"])

    def test_in_development_property(self):
        versions = self.versioninfo.in_development
        self.assertEqual(
            [version.name for version in versions],
            ["branch-with/slash", "master"],
        )

    def test_vhasdoc(self):
        self.assertTrue(self.versioninfo.vhasdoc("master"))
        self.assertFalse(self.versioninfo.vhasdoc("v0.1.0"))
        self.assertTrue(self.versioninfo.vhasdoc("branch-with/slash"))

        self.versioninfo.context["pagename"] = "appendix/faq"
        self.assertTrue(self.versioninfo.vhasdoc("master"))
        self.assertTrue(self.versioninfo.vhasdoc("v0.1.0"))
        self.assertFalse(self.versioninfo.vhasdoc("branch-with/slash"))

    def test_vpathto(self):
        self.assertEqual(self.versioninfo.vpathto("master"), "testpage.html")
        self.assertEqual(
            self.versioninfo.vpathto("v0.1.0"),
            posixpath.join("..", "v0.1.0", "index.html"),
        )
        self.assertEqual(
            self.versioninfo.vpathto("branch-with/slash"),
            posixpath.join("..", "branch-with/slash", "testpage.html"),
        )

        self.versioninfo.context["pagename"] = "appendix/faq"
        self.assertEqual(self.versioninfo.vpathto("master"), "faq.html")
        self.assertEqual(
            self.versioninfo.vpathto("v0.1.0"),
            posixpath.join("..", "..", "v0.1.0", "appendix", "faq.html"),
        )
        self.assertEqual(
            self.versioninfo.vpathto("branch-with/slash"),
            posixpath.join("..", "..", "branch-with/slash", "index.html"),
        )


def version_info_factory(name):

    version_info = {
        "name": name,
        "version": "",
        "release": "0.2",
        "is_released": True,
        "source": "heads",
        "creatordate": "2020-08-07 07:45:20 -0700",
        "basedir": "/dev/null",
        "sourcedir": "/dev/null",
        "outputdir": "/dev/null",
        "confdir": "/dev/null",
        "docnames": ["testpage", "appendix/faq"],
        "commit": 0x1233456,
    }

    return version_info


def test_sorting():

    versions = [
        "2.3.3",
        "2.3.1",
        "2.3.2",
        "2.1.3",
        "0",
        "9",
        "1.1",
        "1.2",
        "1.20",
        "2.2",
        "2.3",
        "2.9.0",
        "2.9.x",
        "2.9.4",
        "master",
        "4",
        "5.2",
    ]

    sorted_versions = sorted(versions, key=normalize_version)

    metadata = {}
    for version in versions:
        metadata[version] = version_info_factory(version)
        
    version_info = sphinx_multiversion.sphinx.VersionInfo(
        app=None,
        context={"pagename": "testpage"},
        metadata=metadata,
        current_version_name="master",
    )

    releases = []
    for vi in version_info.releases:
        releases.append(vi.name)
    assert releases == sorted_versions

    branches = []
    for vi in version_info.branches:
        branches.append(vi.name)
    assert branches == sorted_versions
