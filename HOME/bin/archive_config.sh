# disable-copyfile prevents getting extended attribute files on mac
tar czvf ~/config.tar.gz \
--exclude-from ~/.gitignore_global \
--disable-copyfile \
-C ~ \
 bin/ \
 .bash_profile \
 .gitconfig \
 .gitignore_global \
 .hgrc \
 .hgignore_global \
 .subversion/config \
 .screenrc \
 .vimrc \
"$HOME/Library/Application Support/Sublime Text 3/Packages/User/"
