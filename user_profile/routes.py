from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_connect
from app import login_required
from .utils import save_profile_picture

profile_bp = Blueprint("profile", __name__, template_folder="templates")

@profile_bp.route("/profile")
@login_required
def view_profile():
   user_id = session.get("user_id")
   con = get_connect()
   cur = con.cursor()
   profile = cur.execute("SELECT * from user_profile WHERE user_id = ?", (user_id,)).fetchone()
   cur.close()
   con.close()
   return render_template("user_profile.html", profile=profile)

@profile_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
   user_id = session.get("user_id")
   if request.method == "POST":
      name = request.form.get("name")
      institution = request.form.get("institution")
      birth_date = request.form.get("birth_date")
      bio = request.form.get("bio")
      country = request.form.get("country")
      city = request.form.get("city")
      state = request.form.get("state")

      profile_picture_file = request.files.get("profile_picture")
      profile_picture_path = None

      if profile_picture_file:
         profile_picture_path = save_profile_picture(profile_picture_file, user_id)
      #

      con = get_connect()
      cur = con.cursor()

      if profile_picture_path:
         cur.execute("""
         UPDATE user_profile
            SET name = ?, institution = ?, birth_date = ?, bio = ?, country = ?, city = ?, state = ?, profile_picture = ?
            WHERE user_id = ?
         """, (name, institution, birth_date, bio, country, city, state, profile_picture_path, user_id))
      else:
         cur.execute("""
         UPDATE user_profile
            SET name = ?, institution = ?, birth_date = ?, bio = ?, country = ?, city = ?, state = ?
            WHERE user_id = ?
         """, (name, institution, birth_date, bio, country, city, state, user_id))

      con.commit()
      cur.close()
      con.close()
   
   return redirect(url_for("profile.view_profile"))
