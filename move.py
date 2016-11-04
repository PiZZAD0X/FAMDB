import json
from pathlib import Path
from shutil import copyfile

import utils


def handleMove(environ, start_response):
    user = environ['user']
    missionJsonString = utils.environToContents(environ)
    missionJson = json.loads(missionJsonString)
    missionId = missionJson['missionId']
    versionId = missionJson['versionId']
    # If you're a MM user and this is your mission, or you're a low admin
    if not (utils.checkUserPermissions(user, 1, missionId=missionId, collector=utils.AND) or utils.checkUserPermissions(
            user, 2)):
        start_response("403 Permission Denied", [])
        return ["Access Denied"]

    c = utils.getCursor()
    c.execute("select name from versions where id = ?", [versionId])

    fileName = c.fetchone()[0]
    if Path(utils.missionMakerDir + "/" + fileName).is_file():
        copyfile(utils.missionMakerDir + "/" + fileName, utils.missionMainDir + "/" + fileName)
        c.execute("update versions set existsOnMain=1 where id = ?", [versionId])
        c.connection.commit()
        c.connection.close()

    start_response("200 OK", [])
    return []
