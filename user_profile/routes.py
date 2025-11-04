from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_connect
from decorators import login_required
from .utils import save_profile_picture
profile_bp = Blueprint("profile", __name__, template_folder="templates")
@profile_bp.route("/profile", methods=["GET", "POST"])
@login_required
def view_profile():
   user_id = session.get("user_id")
   con = get_connect()
   cur = con.cursor()
   profile = cur.execute("SELECT * from user_profile WHERE user_id = ?", (user_id,)).fetchone()
   
   if request.method == "POST":
      user_id = session.get("user_id")
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
      
      if profile:

         if profile:
            name = name or profile["name"]
            institution = institution or profile["institution"]
            birth_date = birth_date or profile["birth_date"]
            bio = bio or profile["bio"]
            country = country or profile["country"]
            city = city or profile["city"]
            state = state or profile["state"]

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
      
      else:
         
         if profile_picture_path:
            cur.execute("""
               INSERT INTO user_profile (user_id, name, institution, birth_date, bio, country, city, state, profile_picture)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, name, institution, birth_date, bio, country, city, state, profile_picture_path))
         
         else:
            cur.execute("""
               INSERT INTO user_profile (user_id, name, institution, birth_date, bio, country, city, state)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, name, institution, birth_date, bio, country, city, state))
      
      con.commit()
      cur.close()
      con.close()
      
      return redirect(url_for("profile.view_profile"))
   
   cur.close()
   con.close()
   
   return render_template("user_profile.html", profile=profile)