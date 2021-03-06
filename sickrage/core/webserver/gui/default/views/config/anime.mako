<%inherit file="../layouts/main.mako"/>
<%!
    import sickrage
    from sickrage.core.helpers import anon_url
%>

<%block name="content">
    <div id="config">
        <form id="configForm" action="saveAnime" method="post">
            <ul class="nav nav-tabs">
                <li class="active"><a data-toggle="tab" href="#core-tab-pane1">AnimeDB Settings</a></li>
                <li><a data-toggle="tab" href="#core-tab-pane2">Look &amp; Feel</a></li>
            </ul>

            <div class="tab-content">
                <div id="core-tab-pane1" class="tab-pane fade in active">
                    <div class="tab-pane-desc">
                        <img class="notifier-icon" src="${srWebRoot}/images/anidb24.png" alt="AniDB" title="AniDB"
                             width="24" height="24"/>
                        <h3><a href="${anon_url('http://anidb.info')}"
                               onclick="window.open(this.href, '_blank'); return false;">AniDB</a></h3>
                        <p>AniDB is non-profit database of anime information that is freely open to the public</p>
                    </div>

                    <fieldset class="tab-pane-list">
                        <div class="field-pair">
                            <input type="checkbox" class="enabler" name="use_anidb"
                                   id="use_anidb" ${('', 'checked="checked"')[bool(sickrage.srCore.srConfig.USE_ANIDB)]} />
                            <label for="use_notifo">
                                <span class="component-title">Enable</span>
                                <span class="component-desc">Should SickRage use data from AniDB?</span>
                            </label>
                        </div>

                        <div id="content_use_anidb">
                            <div class="field-pair">
                                <label class="nocheck">
                                    <span class="component-title">AniDB Username</span>
                                    <input type="text" name="anidb_username" id="anidb_username"
                                           value="${sickrage.srCore.srConfig.ANIDB_USERNAME}"
                                           class="form-control input-sm input350"
                                           autocapitalize="off"/>
                                </label>
                                <label class="nocheck">
                                    <span class="component-title">&nbsp;</span>
                                    <span class="component-desc">Username of your AniDB account</span>
                                </label>
                            </div>

                            <div class="field-pair">
                                <label class="nocheck">
                                    <span class="component-title">AniDB Password</span>
                                    <input type="password" name="anidb_password" id="anidb_password"
                                           value="${sickrage.srCore.srConfig.ANIDB_PASSWORD}"
                                           class="form-control input-sm input350"
                                           autocapitalize="off"/>
                                </label>
                                <label class="nocheck">
                                    <span class="component-title">&nbsp;</span>
                                    <span class="component-desc">Password of your AniDB account</span>
                                </label>
                            </div>
                            <div class="field-pair">
                                <input type="checkbox" name="anidb_use_mylist"
                                       id="anidb_use_mylist" ${('', 'checked="checked"')[bool(sickrage.srCore.srConfig.ANIDB_USE_MYLIST)]}/>
                                <label>
                                    <span class="component-title">AniDB MyList</span>
                                    <span class="component-desc">Do you want to add the PostProcessed Episodes to the MyList ?</span>
                                </label>
                            </div>
                        </div>
                        <input type="submit" class="btn config_submitter" value="Save Changes"/>
                    </fieldset>

                </div><!-- /tab-pane //-->

                <div id="core-tab-pane2" class="tab-pane fade">

                    <div class="tab-pane-desc">
                        <h3>Look and Feel</h3>
                    </div>
                    <fieldset class="tab-pane-list">
                        <div class="field-pair">
                            <input type="checkbox" class="enabler" name="split_home"
                                   id="split_home" ${('', 'checked="checked"')[bool(sickrage.srCore.srConfig.ANIME_SPLIT_HOME)]}/>
                            <label for="use_notifo">
                                <span class="component-title">Split show lists</span>
                                <span class="component-desc">Separate anime and normal shows in groups</span>
                            </label>
                        </div>
                        <input type="submit" class="btn config_submitter" value="Save Changes"/>
                    </fieldset>
                </div><!-- /tab-pane //-->
            </div><!-- /ui-components //-->
            <br><input type="submit" class="btn config_submitter" value="Save Changes"/><br>
        </form>
    </div>
</%block>