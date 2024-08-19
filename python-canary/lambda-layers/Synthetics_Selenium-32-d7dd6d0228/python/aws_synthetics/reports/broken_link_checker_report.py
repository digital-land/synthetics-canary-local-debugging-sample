import json
from .synthetics_link import SyntheticsLink
from ..common.utils import ComplexEncoder


class BrokenLinkCheckerReport:
    """
        This class handles the creation of broken link checker report.
        This report can be published and added to Synthetics report.
    """

    def __init__(self):
        self.links = {}
        self.brokenLinks = []
        self.totalLinksChecked = 0
        self.totalBrokenLinks = 0

    def addLink(self, syntheticsLink: SyntheticsLink, isBrokenLink=False):
        """
            Adds a link to BrokenLinkCheckerResult.
            A Link is considered broken if status code is not available or status code >= 300
        """
        self.totalLinksChecked += 1
        syntheticsLink.with_link_num(self.totalLinksChecked)
        if syntheticsLink is not None:
            linkUrl = syntheticsLink.get_url()
            self.links[linkUrl] = syntheticsLink

            linkStatus = syntheticsLink.get_status_code()
            if not isBrokenLink and (not linkStatus or linkStatus >= 400):
                isBrokenLink = True

            if isBrokenLink:
                self.brokenLinks.append(linkUrl)
                self.totalBrokenLinks += 1

    def getLinks(self):
        return self.links

    def getTotalBrokenLinks(self):
        return self.totalBrokenLinks

    def getTotalLinksChecked(self):
        return self.totalLinksChecked

    def reset(self):
        self.links = {}
        self.brokenLinks = []
        self.totalLinksChecked = 0
        self.totalBrokenLinks = 0

    def toDict(self):
        return dict(
            links=self.links,
            brokenLinks=self.brokenLinks,
            totalLinksChecked=self.totalLinksChecked,
            totalBrokenLinks=self.totalBrokenLinks
        )

    def toJson(self):
        return json.dumps(self.toDict(), indent=2, cls=ComplexEncoder)

